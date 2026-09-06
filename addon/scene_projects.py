"""Local scene project catalog. Blender calls belong on the main thread only."""
import datetime
import json
import re
import uuid
from pathlib import Path

class ProjectStore:
    def __init__(self, root):
        self.root=Path(root);self.directory=self.root/'projects/library';self.directory.mkdir(parents=True,exist_ok=True)
        self.index=self.root/'projects/index.json';self.cache={}
        self.catalog=json.loads(self.index.read_text(encoding='utf-8')) if self.index.exists() else {'version':1,'active':None,'projects':[]}

    def persist(self):
        tmp=self.index.with_suffix('.json.tmp');tmp.write_text(json.dumps(self.catalog,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(self.index)

    def entry(self, project_id):
        if not isinstance(project_id,str) or not re.fullmatch(r'[a-z0-9-]{1,64}',project_id):raise ValueError('无效项目编号')
        result=next((p for p in self.catalog['projects'] if p['id']==project_id),None)
        if result is None:raise ValueError('项目不存在，请刷新项目列表')
        return result

    def path(self, project_id):
        self.entry(project_id)
        folder=self.directory/project_id
        if not folder.resolve().is_relative_to(self.directory.resolve()):raise ValueError('项目路径超出目录')
        return folder/'scene.blend'

    def public(self):
        return {'active':self.catalog['active'],'items':[dict(p,available=self.path(p['id']).is_file()) for p in self.catalog['projects']]}

    def add(self,name,description='',project_id=None):
        name=str(name).strip()[:80];description=str(description).strip()[:2000]
        if not name:raise ValueError('请填写项目名称')
        project_id=project_id or uuid.uuid4().hex[:12]
        if not re.fullmatch(r'[a-z0-9-]{1,64}',project_id) or any(p['id']==project_id for p in self.catalog['projects']):raise ValueError('项目编号已存在或无效')
        stamp=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        p={'id':project_id,'name':name,'description':description,'created_at':stamp,'updated_at':stamp}
        self.catalog['projects'].append(p);return p

    def write_scene(self,scene,project_id):
        import bpy
        p=self.entry(project_id);dest=self.path(project_id);dest.parent.mkdir(parents=True,exist_ok=True)
        scene['dkyj_project_id']=project_id
        for ob in scene.objects:ob['dkyj_saved_name']=ob.name
        tmp=dest.with_name('scene.pending.blend')
        # Only this scene and its dependencies: other cached projects stay private.
        bpy.data.libraries.write(str(tmp),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
        if dest.exists():
            import shutil
            shutil.copy2(dest,dest.with_name('scene.previous.blend'))
        tmp.replace(dest)
        p['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        self.cache[project_id]=scene
        self.persist()

    def load(self,project_id):
        import bpy
        self.entry(project_id)
        if project_id in self.cache and self.cache[project_id].name in bpy.data.scenes:return self.cache[project_id]
        file=self.path(project_id)
        if not file.is_file():raise ValueError('项目文件不存在；当前场景保持不变')
        with bpy.data.libraries.load(str(file),link=False) as (data,loaded):
            if not data.scenes:raise ValueError('项目文件中没有场景')
            original_names=set(data.objects)
            loaded.scenes=[data.scenes[0]]
        scene=loaded.scenes[0]
        # Blender adds suffixes when different projects have identically named objects.
        names={}
        for o in scene.objects:
            original=o.get('dkyj_saved_name')
            if not original:
                candidates=[n for n in original_names if o.name==n or re.fullmatch(re.escape(n)+r'\.\d{3,}',o.name)]
                original=max(candidates,key=len) if candidates else o.name
            names[original]=o.name
            o['dkyj_saved_name']=o.name
        take=scene.get('previs_last_take')
        if take in names:scene['previs_last_take']=names[take]
        subjects=json.loads(scene.get('previs_subjects','[]'))
        for subject in subjects:
            if subject.get('object') in names:subject['object']=names[subject['object']]
        if subjects:scene['previs_subjects']=json.dumps(subjects,ensure_ascii=False)
        p=self.entry(project_id);scene['previs_title']=p['name'];scene['previs_subtitle']=p['description']
        scene['dkyj_project_id']=project_id;self.cache[project_id]=scene
        return scene

    def attach(self,scene):
        project_id=scene.get('dkyj_project_id')
        if project_id and any(p['id']==project_id for p in self.catalog['projects']):
            self.cache[project_id]=scene
        else:
            p=self.add(scene.get('previs_title','我的场景'),scene.get('previs_subtitle',''));project_id=p['id'];self.write_scene(scene,project_id)
        self.catalog['active']=project_id
        # Seed examples once, copying their saved models; never regenerate on switch.
        for pid,name,desc,file in [('steamship','蒸汽小船','船舱跑向甲板，飞机掠过。','steamship_scene.blend'),('room','室内排练','桌椅、窗户与两名角色的走位排练。','calibration_scene.blend')]:
            source=self.root/'examples'/file
            if source.exists() and not any(p['id']==pid for p in self.catalog['projects']):
                import shutil
                self.add(name,desc,pid);dest=self.path(pid);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
        self.persist();return project_id

    def create(self,current_scene,name,description='',source='current'):
        import shutil
        if source!='current':self.entry(source)
        p=self.add(name,description);pid=p['id'];dest=self.path(pid);dest.parent.mkdir(parents=True,exist_ok=True)
        try:
            if source=='current':
                # Snapshot then load independently, including independent mesh/action data.
                import bpy
                for ob in current_scene.objects:ob['dkyj_saved_name']=ob.name
                bpy.data.libraries.write(str(dest),{current_scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
            else:shutil.copy2(self.path(source),dest)
            self.persist();scene=self.load(pid);scene['previs_title']=p['name'];scene['previs_subtitle']=p['description']
            self.write_scene(scene,pid);return pid,scene
        except Exception:
            self.catalog['projects'].remove(p);self.persist()
            raise

    def metadata(self,project_id,name,description):
        p=self.entry(project_id)
        name=str(name).strip()[:80]
        if not name:raise ValueError('请填写项目名称')
        p['name']=name;p['description']=str(description).strip()[:2000];self.persist()
