"""Native Blender/GPU regression. Launch without --background, in a separate factory process.
blender --factory-startup --python scripts/test_live_deletion.py
Writes evidence under qa/live-deletion; never opens or changes user projects.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
import urllib.request
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/live-deletion';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'addon'))
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('dkyj_live_deletion_test',ROOT/'addon/whitebox_webcam.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
temp=tempfile.TemporaryDirectory(prefix='dkyj-live-deletion-')
module.ROOT=Path(temp.name);module.RUNTIME=module.ROOT/'runtime';module.TAKES=module.ROOT/'takes'
module.WEB=ROOT/'web'
module.register()

class TestViewfinder(module.Viewfinder):
    def start_http(self, port, cert=None, key=None):
        super().start_http(0, cert, key)

service=None;step=0;started=time.monotonic();results=[];url=None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))

def send(event):
    request=urllib.request.Request(url.replace('/api/state','/api/control'),data=json.dumps(event).encode(),headers={'Content-Type':'application/json'})
    with opener.open(request,timeout=3) as response:assert response.status==202

def state():
    with opener.open(url,timeout=3) as response:return json.load(response)

def finish(error=None):
    global service
    result={'ok':error is None,'checks':results,'blender':bpy.app.version_string,'error':error}
    (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print('LIVE_DELETION_RESULT',json.dumps(result,ensure_ascii=False),flush=True)
    if service:service.close()
    module.SERVICE=None
    module.unregister()
    temp.cleanup()
    bpy.ops.wm.quit_blender()

def run():
    global service,step,url
    try:
        if time.monotonic()-started>50:raise AssertionError('GPU/timer verification timed out at step '+str(step))
        if step==0:
            window=bpy.context.window_manager.windows[0]
            area=next(a for a in window.screen.areas if a.type=='VIEW_3D')
            region=next(r for r in area.regions if r.type=='WINDOW')
            scene=window.scene;scene.camera=bpy.data.objects['Camera'];scene.camera.name='Camera_Phone'
            scene.frame_end=240
            with bpy.context.temp_override(window=window,area=area,region=region):service=TestViewfinder(bpy.context)
            module.SERVICE=service
            url='http://127.0.0.1:%d/api/state?token=%s'%(service.servers[0].server_port,service.token)
        elif step==1:
            if not service.frame_bytes or not service.overview_bytes:return .2
            assert state()['connected'];results.append('native GPU and HTTP frames ready')
            for _ in range(3):
                service.process({'type':'record'});service.scene.frame_set(2);service.record_key();service.process({'type':'stop'})
        elif step==2:
            for camera in list(service.scene.objects):
                if camera.name.startswith('Camera_Take_'):bpy.data.objects.remove(camera,do_unlink=True)
        elif step==3:
            d=state();assert d['connected'] and d['camera']=='Camera_Phone' and d['recorded_take'] is None,d.get('error')
            assert service.frame_bytes and service.overview_bytes
            results.append('delete multiple takes while HTTP/GPU remain connected')
            send({'type':'record'})
        elif step==4:
            assert state()['recording']
            bpy.data.objects.remove(service.scene.camera,do_unlink=True)
        elif step==5:
            d=state();assert not d['recording'] and d['camera']=='Camera_Phone',d.get('error')
            assert service.scene.camera.animation_data is None
            results.append('deleting active recording stops without keying phone')
            send({'type':'record'})
        elif step==6:
            assert state()['recording'];send({'type':'stop'})
        elif step==7:
            d=state();assert not d['recording'] and d['recorded_take']['frames']>=2
            results.append('new take records and stops through HTTP')
            bpy.data.scenes.remove(service.overview_rig.scene)
        elif step==8:
            assert service.overview_rig.is_valid() and service.overview_bytes
            results.append('deleted overview rebuilds with live GPU frames')
            old=service.scene
            replacement=bpy.data.scenes.new('ReplacementScene')
            for ob in list(old.objects):replacement.collection.objects.link(ob)
            replacement.camera=old.camera
            service.window.scene=replacement
            name=old.name;bpy.data.scenes.remove(old);replacement.name=name
        elif step==9:
            assert service.overview_rig.is_valid()
            assert service.overview_rig.source_scene==service.scene
            assert state()['connected'] and service.frame_bytes and service.overview_bytes
            results.append('same-name replacement scene rebinds live view')
            # Verify actual Undo callbacks invalidate GPU resources before RNA changes.
            bpy.ops.ed.undo_push(message='DKYJ before deletion')
            camera=service.scene.camera
            bpy.data.objects.remove(camera,do_unlink=True)
            bpy.ops.ed.undo_push(message='DKYJ camera deleted')
            bpy.ops.ed.undo()
        elif step==10:
            if not service.frame_bytes or not service.overview_bytes:return .2
            assert state()['connected'] and service.overview_rig.is_valid()
            results.append('actual Blender undo recovers timer and GPU views')
            (OUT/'pov-after.png').write_bytes(service.frame_bytes)
            (OUT/'overview-after.png').write_bytes(service.overview_bytes)
            finish();return None
        step+=1
        return .6
    except Exception:
        finish(traceback.format_exc());return None

bpy.app.timers.register(run,first_interval=1)
