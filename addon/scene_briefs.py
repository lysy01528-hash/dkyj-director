"""Durable, data-only scene briefs for a user's external agent."""
import datetime,json,re
from pathlib import Path

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
class BriefStore:
    def __init__(self,root):
        self.path=Path(root)/'projects/briefs.json';self.path.parent.mkdir(parents=True,exist_ok=True)
        self.data=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {'revision':0,'items':[]}
    def save(self):
        self.data['revision']+=1;p=self.path.with_suffix('.pending');p.write_text(json.dumps(self.data,ensure_ascii=False,indent=2), encoding='utf-8');p.replace(self.path)
    def find(self,id):
        found=next((b for b in self.data['items'] if b['id']==id),None)
        if not found:raise ValueError('创作任务不存在')
        return found
    def create(self,e):
        id=e.get('id','')
        if not re.fullmatch(r'[a-z0-9-]{8,64}',id):raise ValueError('无效任务编号')
        if any(b['id']==id for b in self.data['items']):return self.find(id)
        fields={k:str(e.get(k,'')).strip()[:limit] for k,limit in [('scene',2000),('characters',1000),('action',2000),('camera',1000),('source',64)]}
        if not fields['scene'] or not fields['characters'] or not fields['action']:raise ValueError('请补充场景、人物和动作描述')
        b=dict(id=id,**fields,status='waiting',project_id=None,created_at=stamp(),updated_at=stamp(),messages=[],verification='')
        self.data['items'].append(b);self.save();return b
    def update(self,e):
        b=self.find(e.get('id'));status=e.get('status',b['status']);message=str(e.get('message','')).strip()[:2000]
        if status not in {'waiting','working','needs_input','ready','failed'}:raise ValueError('无效任务状态')
        if status=='ready' and b['status']!='working':raise ValueError('请先制作并检查场景，再完成任务')
        if status=='ready' and (not e.get('project_id',b['project_id']) or not str(e.get('verification','')).strip()):raise ValueError('完成任务需要项目编号与验证说明')
        b['status']=status;b['updated_at']=stamp()
        if e.get('project_id'):b['project_id']=e['project_id']
        if e.get('verification'):b['verification']=str(e['verification'])[:2000]
        if message:b['messages'].append({'role':'agent','text':message,'at':stamp()})
        self.save()
    def reply(self,e):
        b=self.find(e.get('id'));message=str(e.get('message','')).strip()[:2000]
        if not message:raise ValueError('请填写补充说明')
        if b['status']=='working':raise ValueError('Agent 正在制作，请等它完成或提出问题后再补充')
        b['messages'].append({'role':'user','text':message,'at':stamp()});b['status']='waiting';b['updated_at']=stamp();self.save()
