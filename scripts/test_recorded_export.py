"""Regression checks for recorded-take ownership and export camera selection."""
import collections, importlib.util, json, time
from pathlib import Path
from types import SimpleNamespace
import bpy
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / 'recorded-export-regression'
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('webcam_under_test', ROOT / 'addon' / 'whitebox_webcam.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
if not hasattr(module.Viewfinder, 'recorded_take_info'):
    raise AssertionError('backend is not ready: recorded_take_info is missing')

def make_service():
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    data = bpy.data.cameras.new('PhoneCameraData')
    cam = bpy.data.objects.new('Camera_Phone', data); scene.collection.objects.link(cam)
    cam.location = (0, -8, 3); cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = Quaternion((1, 0, 0, 0)); scene.camera = cam
    scene.frame_start, scene.frame_end = 1, 48; scene.frame_set(1)
    area = SimpleNamespace(type='VIEW_3D', tag_redraw=lambda: None)
    s = module.Viewfinder.__new__(module.Viewfinder)
    s.window = SimpleNamespace(scene=scene, view_layer=bpy.context.view_layer, screen=SimpleNamespace(areas=[area]))
    s.area, s.region, s.space = area, None, None
    s.events = collections.deque(); s.closed = s.recording = s.playing = False
    s.take_name = ''; s.take_start = s.take_end = 1; s.last_record_frame = -1
    s.last_record_quaternion = None; s.camera_resets = {}; s.sensor_base = None
    s.control_hold = False; s.speed = 1.5; s.last_input = time.monotonic()
    s.last_tick = time.monotonic(); s.move = Vector((0, 0, 0))
    s.export_process = None; s.export_state = {'status': 'idle'}; s.error = ''
    s.stream_fps = 0; s.http_url = s.https_url = ''; s.capture_busy = False
    return s, scene, cam

class FakeProcess:
    def __init__(self, args): self.args, self.returncode = list(args), None
    def poll(self): return None

def motion(obj):
    scene = bpy.context.scene; out = []
    for frame in (int(obj.get('previs_take_start', 1)), int(obj.get('previs_take_end', 1))):
        scene.frame_set(frame); bpy.context.view_layer.update()
        out.append((obj.matrix_world.translation.copy(), obj.matrix_world.to_quaternion().copy()))
    return out

s, scene, original = make_service()
result = {'ok': False, 'checks': {}}

s.begin_export()
assert s.export_state.get('status') == 'error', s.export_state
assert s.export_process is None
result['checks']['no_take_export_rejected'] = True

scene.frame_set(1); s.process({'type': 'record'}); take = scene.camera
assert take.name == s.take_name
for frame in range(2, 25):
    scene.frame_set(frame); take.location.x = frame * 0.05
    take.rotation_mode = 'QUATERNION'; take.rotation_quaternion = Quaternion((0, 0, 1), frame * 0.015)
    s.record_key()
s.process({'type': 'stop'}); assert s.control_hold is True
before = motion(take)
for _ in range(20):
    s.process({'type': 'orientation', 'quaternion': [0.05, 0.1, 0.02, 0.99]})
assert scene.camera == take and not any(o.name == 'Camera_Live' for o in bpy.data.objects)
after = motion(take)
for a, b in zip(before, after):
    assert (a[0] - b[0]).length < 1e-6 and a[1].rotation_difference(b[1]).angle < 1e-6
info = s.recorded_take_info()
assert info and info['name'] == take.name and info['frames'] >= 24 and info['has_motion']
result['checks']['post_stop_sensor_hold'] = True; result['take_info'] = info

s.process({'type': 'resume_live'}); live = scene.camera
assert live.name == 'Camera_Phone' and not live.get('previs_take_start')
assert s.recorded_take_info(take.name)['name'] == take.name
result['checks']['resume_live_explicit'] = True

old_popen = module.subprocess.Popen
module.subprocess.Popen = lambda args, **kwargs: FakeProcess(args)
module.TAKES = OUT
try:
    s.begin_export()
finally:
    module.subprocess.Popen = old_popen
assert s.export_process is not None
command = s.export_process.args
assert take.name in command, command
assert s.export_name.endswith('.mp4')
scene.camera = take; sampled = []
for frame in (int(info['start']), int(info['end'])):
    scene.frame_set(frame); bpy.context.view_layer.update()
    sampled.append({'frame': frame, 'location': list(take.matrix_world.translation),
                    'rotation_quaternion': list(take.matrix_world.to_quaternion())})
assert sampled[0]['location'] != sampled[-1]['location']
assert sampled[0]['rotation_quaternion'] != sampled[-1]['rotation_quaternion']
result['checks']['export_binds_recorded_take'] = True
take_name = take.name
snapshot_path = str(command[3])
bpy.ops.wm.open_mainfile(filepath=snapshot_path)
loaded_scene = bpy.context.scene
loaded_camera = loaded_scene.camera
assert loaded_camera and loaded_camera.name == take_name, (loaded_camera.name if loaded_camera else None, take_name)
loaded_samples = []
for frame in (int(info['start']), int(info['end'])):
    loaded_scene.frame_set(frame); bpy.context.view_layer.update()
    loaded_samples.append({'frame': frame, 'location': list(loaded_camera.matrix_world.translation),
                           'rotation_quaternion': list(loaded_camera.matrix_world.to_quaternion())})
assert loaded_camera.animation_data and loaded_camera.animation_data.action
assert loaded_samples[0]['location'] != loaded_samples[-1]['location']
assert loaded_samples[0]['rotation_quaternion'] != loaded_samples[-1]['rotation_quaternion']
result['checks']['snapshot_reopens_with_recorded_camera'] = True
result['export'] = {'command': [str(x) for x in command], 'name': take_name,
                    'snapshot': snapshot_path, 'camera': take_name,
                    'samples_before_reopen': sampled, 'samples_loaded_snapshot': loaded_samples}
result['ok'] = True
(OUT / 'recorded-export-regression.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print('RECORDED_EXPORT_REGRESSION', json.dumps(result, ensure_ascii=False))
