"""Run with Blender --background --factory-startup --python-exit-code 1 --python."""
import bpy,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'addon'))
from scene_projects import ProjectStore
with tempfile.TemporaryDirectory() as directory:
    store=ProjectStore(directory);scene=bpy.context.scene;scene.camera=bpy.data.objects['Camera'];camera=scene.camera
    camera['previs_take_start']=1;camera['previs_take_end']=24;scene['previs_last_take']=camera.name
    scene['previs_subjects']=json.dumps([{'object':camera.name,'name':'test'}])
    for f,x in [(1,0),(24,4)]:camera.location.x=x;camera.keyframe_insert('location',frame=f)
    first=store.attach(scene);pid,copy=store.create(scene,'Second','Test copy')
    assert copy!=scene and copy.camera!=camera and copy.camera.data!=camera.data
    assert copy.camera.animation_data.action!=camera.animation_data.action
    assert copy['previs_last_take']==copy.camera.name
    assert json.loads(copy['previs_subjects'])[0]['object']==copy.camera.name
    copy.camera.data.lens=70;assert camera.data.lens!=70
    store.write_scene(copy,pid);store.catalog['active']=pid;store.persist()
    fresh=ProjectStore(directory);restored=fresh.load(pid)
    assert restored.camera.data.lens==70 and restored['previs_last_take']==restored.camera.name
    bpy.context.window.scene=restored
    samples=[]
    for f in [1,24]:restored.frame_set(f);samples.append(restored.camera.location.x)
    assert abs(samples[1]-samples[0]-4)<.001,samples
    assert fresh.catalog['active']==pid and fresh.entry(pid)['description']=='Test copy'
    # Deleted cached Scene wrappers must fall back to the on-disk project.
    bpy.context.window.scene=scene
    bpy.data.scenes.remove(restored)
    replacement=fresh.load(pid)
    assert replacement.camera.data.lens==70
    assert fresh.scene_is_live(replacement)
    try:fresh.write_scene(restored,pid);raise AssertionError('removed scene accepted')
    except ValueError:pass
    try:store.path('../escape');raise AssertionError('path accepted')
    except ValueError:pass
    # Missing project files cannot silently substitute another scene.
    missing=store.add('Missing')['id']
    try:store.load(missing);raise AssertionError('missing accepted')
    except ValueError:pass
print('PROJECT_TESTS_OK independent scene/mesh/action, disk reload, camera/subject remap, motion, metadata, path guard')
