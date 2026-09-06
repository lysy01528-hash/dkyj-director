"""Install the DKYJ viewfinder, recording this clone's location locally."""
import json,shutil
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]
target=Path(bpy.utils.user_resource('SCRIPTS',path='addons',create=True))/'whitebox_webcam.py'
shutil.copy2(root/'addon/whitebox_webcam.py',target)
target.with_name('dkyj_workspace.json').write_text(json.dumps({'root':str(root)},ensure_ascii=False),encoding='utf-8')
bpy.utils.refresh_script_paths()
if 'whitebox_webcam' in bpy.context.preferences.addons:bpy.ops.preferences.addon_disable(module='whitebox_webcam')
bpy.ops.preferences.addon_enable(module='whitebox_webcam')
bpy.ops.wm.save_userpref()
print('DKYJ_INSTALLED',target)
