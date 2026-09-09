"""Blender-only, disposable overview cleanup tests; no user file is opened."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'addon'))
from whitebox_overview import OverviewRig, cleanup_saved_overviews

source=bpy.context.scene
source.camera=bpy.data.objects['Camera']
source_names=set(o.name for o in source.objects)
checks=[]
for kind in ['repeat_close','scene','helper','collection','world','camera_data','source']:
    scene=source if kind!='source' else bpy.data.scenes.new('DisposableSource')
    rig=OverviewRig(scene)
    assert rig.is_valid(),kind
    if kind=='scene':bpy.data.scenes.remove(rig.scene)
    if kind=='helper':bpy.data.objects.remove(rig.camera_model,do_unlink=True)
    if kind=='collection':bpy.data.collections.remove(rig.collection)
    if kind=='world':bpy.data.worlds.remove(rig.world)
    if kind=='camera_data':bpy.data.cameras.remove(rig.camera.data)
    if kind=='source':bpy.data.scenes.remove(scene)
    if kind!='repeat_close':assert not rig.is_valid(),kind
    rig.close();rig.close()
    assert not rig.is_valid(),kind
    assert source_names == set(o.name for o in source.objects),kind
    assert not any(s.get('previs_overview_owned') for s in bpy.data.scenes),kind
    assert not any(o.get('previs_overview_owned') for o in bpy.data.objects),kind
    checks.append(kind)
print('OVERVIEW_LIFECYCLE_OK',checks)

# Saved overviews can contain helpers sharing a mesh; the second reference must
# not be dereferenced after the first one has already reclaimed that mesh.
rig=OverviewRig(source)
clone=bpy.data.objects.new('SharedHelperData',rig.camera_model.data)
clone['previs_overview_owned']=True
rig.collection.objects.link(clone)
cleanup_saved_overviews();cleanup_saved_overviews();rig.close()
assert source_names == set(o.name for o in source.objects)
print('SAVED_OVERVIEW_SHARED_DATA_OK')
