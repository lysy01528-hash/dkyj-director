"""Blender regression: delete takes/scenes while the local HTTP connection stays open.
Run: blender --background --factory-startup --python-exit-code 1 --python tests/test_deleted_data.py
All projects and HTTP endpoints here are disposable; no user scene is loaded.
"""
import collections
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
import urllib.request
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'addon'))
spec = importlib.util.spec_from_file_location('webcam_lifecycle_test', ROOT / 'addon/whitebox_webcam.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DeletedDataTests(unittest.TestCase):
    def setUp(self):
        self.previous_scene = bpy.context.window.scene
        self.scene = bpy.data.scenes.new('DKYJ_Delete_Regression')
        bpy.context.window.scene = self.scene
        self.scene.frame_end = 48
        cam = bpy.data.objects.new('Camera_Phone', bpy.data.cameras.new('TestPhoneData'))
        self.scene.collection.objects.link(cam)
        cam.location = (0, -8, 3)
        cam.rotation_mode = 'QUATERNION'
        self.scene.camera = cam
        s = module.Viewfinder.__new__(module.Viewfinder)
        s.window = bpy.context.window
        s.area = next(a for a in s.window.screen.areas if a.type == 'VIEW_3D')
        s.region = next(r for r in s.area.regions if r.type == 'WINDOW')
        s.space = s.area.spaces.active
        s.closed = s.capture_busy = s.recording = s.playing = False
        s.events = collections.deque()
        s.take_name = ''; s.take_start = s.take_end = 1
        s.last_record_frame = -1; s.last_record_quaternion = s.take_first_pose = None
        s.camera_resets = {}; s.sensor_base = None; s.control_hold = False
        s.speed = 1.5; s.move = Vector(); s.last_input = s.last_tick = time.monotonic()
        s.last_draw = 0; s.stream_fps = 0; s.error = ''
        s.export_process = s.export_log = s.export_name = None
        s.export_state = {'status': 'idle'}; s.downloads = set()
        s.offscreen = s.overview_offscreen = s.overview_rig = None
        s.overview_bytes = s.frame_bytes = b''; s.overview_frame = None
        s.overview_error = ''; s.state = {}; s.servers = []
        s.http_url = s.https_url = ''; s.token = 'lifecycle-test-token'
        self.s = s
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        s.start_http(0)
        self.url = 'http://127.0.0.1:%d/api/state?token=%s' % (s.servers[0].server_port, s.token)

    def tearDown(self):
        self.s.dispose_overview()
        for server in self.s.servers:
            server.shutdown(); server.server_close()
        bpy.context.window.scene = self.previous_scene
        for scene in list(bpy.data.scenes):
            if scene.name.startswith('DKYJ_Delete_Regression'):
                for obj in list(scene.objects):
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.scenes.remove(scene)

    def record(self):
        self.s.process({'type': 'record'})
        self.scene.frame_set(2)
        self.scene.camera.location.x += 1
        self.s.record_key()
        self.s.process({'type': 'stop'})
        return self.scene.camera

    def state(self):
        self.s.refresh_state()
        with self.opener.open(self.url, timeout=3) as response:
            return json.load(response)

    def test_delete_all_takes_then_record_again(self):
        for _ in range(3): self.record()
        self.s.prepare_overview()
        for cam in list(self.scene.objects):
            if cam.name.startswith('Camera_Take_'): bpy.data.objects.remove(cam, do_unlink=True)
        self.s.tick()
        self.assertTrue(self.state()['connected'])
        self.assertIsNone(self.state()['recorded_take'])
        self.assertEqual(self.s.take_name, '')
        self.assertEqual(self.scene.camera.name, 'Camera_Phone')
        new = self.record()
        self.assertEqual(self.state()['recorded_take']['name'], new.name)

    def test_delete_recording_camera_does_not_key_another_camera(self):
        self.s.process({'type': 'record'})
        deleted = self.scene.camera
        phone = next(o for o in self.scene.objects if o.name == 'Camera_Phone')
        bpy.data.objects.remove(deleted, do_unlink=True)
        self.scene.camera = phone
        self.s.tick()
        self.assertFalse(self.s.recording)
        self.assertIsNone(phone.animation_data)
        self.assertNotIn('previs_take_start', phone)
        self.record()
        self.assertTrue(self.state()['recorded_take'])

    def test_delete_every_camera_has_recoverable_phone(self):
        self.record()
        for cam in list(self.scene.objects):
            if cam.type == 'CAMERA': bpy.data.objects.remove(cam, do_unlink=True)
        self.s.tick()
        self.assertEqual(self.state()['camera'], 'Camera_Phone')
        self.record()
        self.assertTrue(self.state()['recorded_take'])

    def test_removed_overview_can_rebuild(self):
        self.s.prepare_overview()
        old = self.s.overview_rig
        bpy.data.scenes.remove(old.scene)
        self.s.prepare_overview()
        self.assertIsNot(self.s.overview_rig, old)
        self.assertEqual(self.s.overview_error, '')
        self.assertTrue(self.state()['connected'])

    def test_same_name_recreated_scene_discards_old_rig(self):
        self.s.prepare_overview()
        old = self.s.overview_rig
        old_scene = self.scene
        replacement = bpy.data.scenes.new('DKYJ_Delete_Regression_Replacement')
        for obj in list(old_scene.objects): replacement.collection.objects.link(obj)
        replacement.camera = old_scene.camera
        bpy.context.window.scene = replacement
        name = old_scene.name
        bpy.data.scenes.remove(old_scene)
        replacement.name = name
        self.scene = replacement
        self.s.tick()
        self.assertIsNot(self.s.overview_rig, old)
        self.assertEqual(self.s.overview_rig.source_scene, replacement)
        self.assertTrue(self.state()['connected'])
        self.record()

    def test_stale_scene_state_never_kills_timer(self):
        # Match an RNA wrapper invalidated by deletion/undo before the next tick.
        from types import SimpleNamespace
        stale = bpy.data.scenes.new('DKYJ_Delete_Regression_Stale')
        self.s.window = SimpleNamespace(scene=stale, screen=bpy.context.window.screen,
                                        view_layer=bpy.context.view_layer)
        bpy.data.scenes.remove(stale)
        self.assertIsInstance(self.s.tick(), float)
        self.assertTrue(self.state()['connected'])
        self.record()

    def test_malformed_story_is_not_a_timer_failure(self):
        self.scene['previs_story'] = '1 x invalid'
        self.scene['previs_subjects'] = '{}'
        self.assertIsInstance(self.s.tick(), float)
        self.assertEqual(self.state()['story'], [])
        self.assertEqual(self.state()['subjects'], [])

    def test_deleted_export_target_is_rejected(self):
        take = self.record(); name = take.name
        bpy.data.objects.remove(take, do_unlink=True)
        self.s.tick()
        self.s.begin_export(name)
        self.assertEqual(self.s.export_state['status'], 'error')
        self.assertIsNone(self.s.export_process)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(DeletedDataTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise SystemExit(1)
print('DELETED_DATA_TESTS_OK', result.testsRun)
