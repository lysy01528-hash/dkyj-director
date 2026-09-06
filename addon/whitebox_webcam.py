"""A local web viewfinder for Blender. Browser input is data only; never evaluated as code."""
bl_info = {'name': 'DKYJ Director · 大开眼界导演台', 'author': 'DKYJ Director contributors', 'version': (0, 6, 0),
           'blender': (5, 2, 0), 'location': '3D View > Sidebar > 网页摄影机', 'category': '3D View'}

import collections
import hmac
import http.server
import ipaddress
import json
import math
import mimetypes
import os
import secrets
import socket
import socketserver
import ssl
import struct
import subprocess
import sys
import threading
import time
import urllib.parse
import zlib
from pathlib import Path

import bpy
import gpu
from mathutils import Quaternion, Vector

def workspace_root():
    configured=os.environ.get('DKYJ_HOME')
    config=Path(__file__).with_name('dkyj_workspace.json')
    if not configured and config.exists():configured=json.loads(config.read_text(encoding='utf-8')).get('root')
    return Path(configured).expanduser().resolve() if configured else Path(__file__).resolve().parents[1]

ROOT = workspace_root()
WEB = ROOT / 'web'
RUNTIME = ROOT / 'runtime'
TAKES = ROOT / 'takes'
WIDTH, HEIGHT = 768, 432
SERVICE = None

def overview_module():
    directory = str(ROOT / 'addon')
    if directory not in sys.path:
        sys.path.insert(0, directory)
    import whitebox_overview
    return whitebox_overview

def lan_ip():
    directory = str(ROOT / 'scripts')
    if directory not in sys.path:
        sys.path.insert(0, directory)
    from network_utils import lan_ip as detect_ip
    return detect_ip()

def png_rgba(buffer, width, height):
    # GPU rows run bottom to top. NumPy ships with Blender; avoid an imaging dependency.
    import numpy as np
    pixels = np.asarray(buffer, dtype=np.uint8).reshape(height, width, 4)[::-1]
    raw = b''.join(b'\x00' + row.tobytes() for row in pixels)
    def chunk(kind, content):
        return struct.pack('!I', len(content)) + kind + content + struct.pack('!I', zlib.crc32(kind + content) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 2)) + chunk(b'IEND', b''))

def finite(value, default=0.0, minimum=-1.0, maximum=1.0):
    try:
        number = float(value)
        return max(minimum, min(maximum, number)) if math.isfinite(number) else default
    except (ValueError, TypeError):
        return default

class RequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *_):
        pass

    @property
    def service(self):
        return self.server.service

    def send_bytes(self, status, data, content_type, extra=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        if self.close_connection:
            self.send_header('Connection', 'close')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_json(self, status, data):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False, allow_nan=False).encode(), 'application/json; charset=utf-8')

    def authorized(self):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        supplied = query.get('token', [''])[0]
        if not hmac.compare_digest(supplied, self.service.token):
            self.close_connection = True
            self.send_json(403, {'ok': False, 'error': '配对链接已失效，请从 Blender 重新打开链接。'})
            return False
        origin = self.headers.get('Origin')
        if origin and urllib.parse.urlsplit(origin).netloc != self.headers.get('Host'):
            self.close_connection = True
            self.send_json(403, {'ok': False, 'error': 'Origin mismatch'})
            return False
        return True

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path in ('/', '/index.html', '/app.js', '/app.css', '/overview.js', '/projects.js', '/welcome.js'):
            file = WEB / ('index.html' if path == '/' else path[1:])
            if not file.is_file():
                return self.send_json(503, {'ok': False, 'error': '取景器页面尚未准备好'})
            return self.send_bytes(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'text/plain')
        if not self.authorized():
            return
        if path == '/phone-qr.png':
            mode = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get('mode', ['http'])[0]
            url = self.service.https_url if mode == 'https' else self.service.http_url
            if not url:
                return self.send_json(503, {'ok': False, 'error': 'HTTPS unavailable'})
            cache = getattr(self.service, 'pairing_qr_cache', {})
            if url not in cache:
                python = ROOT / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
                try:
                    result = subprocess.run([str(python), '-c', 'import sys,qrcode; qrcode.make(sys.stdin.read()).save(sys.stdout.buffer, format="PNG")'], input=url.encode(), capture_output=True, timeout=8, check=True)
                    cache[url] = result.stdout
                    self.service.pairing_qr_cache = cache
                except (OSError, subprocess.SubprocessError):
                    return self.send_json(503, {'ok': False, 'error': 'QR unavailable; use pairing link'})
            return self.send_bytes(200, cache[url], 'image/png')
        if path == '/api/state':
            return self.send_json(200, self.service.state)
        if path == '/frame.png':
            if not self.service.frame_bytes:
                return self.send_json(503, {'ok': False, 'error': '等待 Blender 视图绘制'})
            return self.send_bytes(200, self.service.frame_bytes, 'image/png')
        if path == '/overview.png':
            if not self.service.overview_bytes:
                return self.send_json(503, {'ok': False, 'error': '等待空间总览绘制'})
            return self.send_bytes(200, self.service.overview_bytes, 'image/png')
        if path == '/local-camera.mobileconfig':
            file = RUNTIME / 'tls/local-camera.mobileconfig'
            if file.is_file():
                return self.send_bytes(200, file.read_bytes(), 'application/x-apple-aspen-config',
                                       {'Content-Disposition': 'attachment; filename="Blender-Local-Camera.mobileconfig"'})
        if path.startswith('/download/'):
            name = urllib.parse.unquote(path.removeprefix('/download/'))
            if Path(name).name == name and name in self.service.downloads:
                file = TAKES / name
                if file.is_file():
                    return self.send_bytes(200, file.read_bytes(), mimetypes.guess_type(name)[0] or 'application/octet-stream',
                                           {'Content-Disposition': 'attachment; filename="' + name + '"'})
        self.send_json(404, {'ok': False, 'error': 'Not found'})

    def do_POST(self):
        if urllib.parse.urlsplit(self.path).path != '/api/control':
            return self.send_json(404, {'ok': False})
        if not self.authorized():
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 16384:
                raise ValueError('Invalid content length')
            event = json.loads(self.rfile.read(length))
            allowed = {'input', 'orientation', 'sensor_base', 'play', 'pause', 'record', 'stop',
                       'reset_camera', 'seek', 'camera', 'settings', 'export', 'resume_live', 'zones', 'project_save', 'project_switch', 'project_create', 'project_update', 'brief_create', 'brief_update', 'brief_reply'}
            if not isinstance(event, dict) or event.get('type') not in allowed:
                raise ValueError('Unknown command')
            if event['type'] == 'input':
                if len(event.get('move', [])) != 3 or len(event.get('look', [])) != 2:
                    raise ValueError('Invalid input vector')
            if event['type'] == 'orientation' and len(event.get('quaternion', [])) != 4:
                raise ValueError('Invalid orientation')
            self.service.events.append(event)
            self.send_json(202, {'ok': True})
        except (ValueError, TypeError, OverflowError, json.JSONDecodeError) as error:
            self.close_connection = True
            self.send_json(400, {'ok': False, 'error': str(error)})

class LocalHTTPServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        # A local camera never needs reverse DNS. macOS host-name lookup can block
        # Blender's UI thread for minutes before HTTPServer starts listening.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]

class Viewfinder:
    def __init__(self, context):
        self.window = context.window
        self.area = context.area
        self.region = next(r for r in self.area.regions if r.type == 'WINDOW')
        self.space = self.area.spaces.active
        self.token = secrets.token_urlsafe(24)
        # Keep pairing links valid across routine local app restarts.
        try:
            saved_token=json.loads((RUNTIME/'connection.json').read_text(encoding='utf-8')).get('token','')
            if len(saved_token)==32 and all(c.isalnum() or c in '-_' for c in saved_token):self.token=saved_token
        except (OSError, ValueError):pass
        self.ip = lan_ip()
        self.events = collections.deque(maxlen=512)
        self.frame_bytes = b''
        self.overview_bytes = b''
        self.overview_rig = None
        self.overview_offscreen = None
        self.overview_error = ''
        self.overview_frame = None
        self.last_draw = 0.0
        self.last_tick = time.monotonic()
        self.last_input = 0.0
        self.speed = 1.5
        self.move = Vector((0, 0, 0))
        self.playing = False
        self.recording = False
        self.play_started = 0.0
        self.start_frame = 1
        self.last_record_frame = -1
        self.last_record_quaternion = None
        self.take_name = self.scene.get('previs_last_take', '')
        if not self.take_name:
            existing = [o for o in self.scene.objects if o.type == 'CAMERA' and 'previs_take_start' in o]
            if existing:
                self.take_name = max(existing, key=lambda o: o.get('previs_created_at', 0)).name
        self.take_start = 1
        self.take_end = 1
        self.sensor_base = None
        self.control_hold = bool(self.take_name)
        self.take_first_pose = None
        self.camera_resets = {}
        self.error = ''
        self.stream_fps = 0.0
        self.export_state = {'status': 'idle'}
        self.export_process = None
        self.export_log = None
        self.export_name = None
        self.downloads = set()
        self.offscreen = None
        self.capture_busy = False
        self.closed = False
        self.servers = []
        self.http_url = f'http://{self.ip}:8765/?token={self.token}'
        self.https_url = None
        self.state = {}
        overview_module().cleanup_saved_overviews()
        from scene_projects import ProjectStore
        self.projects=ProjectStore(ROOT);self.projects.attach(self.scene)
        self.project_event=0;self.project_message=''
        from scene_briefs import BriefStore
        self.briefs=BriefStore(ROOT)
        RUNTIME.mkdir(exist_ok=True)
        TAKES.mkdir(exist_ok=True)
        self.start_http(8765)
        cert = RUNTIME / 'tls/server.pem'
        key = RUNTIME / 'tls/server-key.pem'
        if cert.exists() and key.exists():
            self.start_http(8766, cert, key)
            self.https_url = f'https://{self.ip}:8766/?token={self.token}'
        self.refresh_state()
        info = {'http_url': self.http_url, 'https_url': self.https_url, 'token': self.token,
                'certificate_profile': self.http_url.replace('/?token=', '/local-camera.mobileconfig?token=')}
        connection = RUNTIME / 'connection.json'
        connection.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
        connection.chmod(0o600)
        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_PIXEL')
        bpy.app.timers.register(self.tick, first_interval=0.05, persistent=True)

    @property
    def scene(self):
        return self.window.scene

    def start_http(self, port, cert=None, key=None):
        server = LocalHTTPServer(('0.0.0.0', port), RequestHandler)
        server.service = self
        try:
            if cert:
                tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                tls.minimum_version = ssl.TLSVersion.TLSv1_2
                tls.load_cert_chain(str(cert), str(key))
                server.socket = tls.wrap_socket(server.socket, server_side=True)
        except Exception:
            server.server_close()
            for running in self.servers:
                running.shutdown()
                running.server_close()
            raise
        self.servers.append(server)
        threading.Thread(target=server.serve_forever, daemon=True).start()

    def camera(self):
        camera = self.scene.camera
        if not camera:
            raise ValueError('请先在 Blender 场景中添加摄影机')
        if camera.name not in self.camera_resets:
            self.camera_resets[camera.name] = camera.matrix_world.copy()
        return camera

    def local_camera(self):
        camera = self.camera()
        if not self.recording and (camera.parent or camera.constraints or (camera.animation_data and camera.animation_data.action)):
            matrix = camera.matrix_world.copy()
            duplicate = camera.copy()
            duplicate.data = camera.data.copy()
            duplicate.animation_data_clear()
            duplicate.data.animation_data_clear()
            duplicate.parent = None
            duplicate.constraints.clear()
            duplicate.name = 'Camera_Live'
            for key in list(duplicate.keys()):
                if key.startswith('previs_take_') or key == 'previs_created_at':
                    del duplicate[key]
            duplicate.matrix_world = matrix
            self.scene.collection.objects.link(duplicate)
            self.scene.camera = duplicate
            camera = duplicate
            self.camera_resets[camera.name] = matrix.copy()
        return camera

    def recorded_take_info(self, name=None):
        camera = self.scene.objects.get(name or self.take_name)
        if (not camera or camera.type != 'CAMERA' or 'previs_take_start' not in camera
                or not camera.animation_data or not camera.animation_data.action):
            return None
        start = int(camera['previs_take_start'])
        end = int(camera.get('previs_take_end', start))
        return {'name': camera.name, 'start': start, 'end': end, 'frames': end - start + 1,
                'duration': (end - start + 1) / (self.scene.render.fps / self.scene.render.fps_base),
                'has_motion': bool(camera.get('previs_take_motion', False))}

    def record_key(self):
        frame = self.scene.frame_current
        camera = self.camera()
        # q and -q are the same orientation, but opposite signs in adjacent
        # component F-curves can produce a spin through zero on playback.
        previous = getattr(self, 'last_record_quaternion', None)
        if previous is not None and camera.rotation_quaternion.dot(previous) < 0:
            camera.rotation_quaternion.negate()
        self.last_record_quaternion = camera.rotation_quaternion.copy()
        if getattr(self, 'take_first_pose', None) is None:
            self.take_first_pose = (camera.location.copy(), camera.rotation_quaternion.copy(), camera.data.lens)
        position, rotation, lens = self.take_first_pose
        if ((camera.location - position).length > 0.0001
                or camera.rotation_quaternion.rotation_difference(rotation).angle > 0.0001
                or abs(camera.data.lens - lens) > 0.001):
            camera['previs_take_motion'] = True
        camera.keyframe_insert(data_path='location', frame=frame)
        camera.keyframe_insert(data_path='rotation_quaternion', frame=frame)
        camera.data.keyframe_insert(data_path='lens', frame=frame)
        self.last_record_frame = frame
        self.take_end = frame
        camera['previs_take_start'] = self.take_start
        camera['previs_take_end'] = self.take_end

    def linearize_take(self):
        camera = self.scene.camera
        if not camera:
            return
        for obj in [camera, camera.data]:
            action = obj.animation_data.action if obj.animation_data else None
            if not action:
                continue
            for layer in action.layers:
                for strip in layer.strips:
                    if strip.type == 'KEYFRAME':
                        bag = strip.channelbag(obj.animation_data.action_slot)
                        if bag:
                            for curve in bag.fcurves:
                                for key in curve.keyframe_points:
                                    key.interpolation = 'LINEAR'

    def process(self, event):
        kind = event['type']
        if kind == 'input':
            if getattr(self, 'control_hold', False):
                self.move = Vector((0, 0, 0))
                return
            self.move = Vector(tuple(finite(x) for x in event['move']))
            self.last_input = time.monotonic()
            yaw, pitch = (finite(x, minimum=-0.4, maximum=0.4) for x in event['look'])
            if yaw or pitch:
                camera = self.local_camera()
                q = camera.matrix_world.to_quaternion()
                q = Quaternion((0, 0, 1), yaw) @ q @ Quaternion((1, 0, 0), pitch)
                camera.rotation_mode = 'QUATERNION'
                camera.rotation_quaternion = q.normalized()
        elif kind == 'sensor_base':
            if getattr(self, 'control_hold', False):
                self.playing = False
            self.control_hold = False
            self.sensor_base = self.local_camera().matrix_world.to_quaternion()
        elif kind == 'resume_live':
            self.playing = False
            self.control_hold = False
            self.sensor_base = None
            self.local_camera()
        elif kind == 'orientation':
            if getattr(self, 'control_hold', False):
                return
            if self.sensor_base is None:
                self.sensor_base = self.local_camera().matrix_world.to_quaternion()
            x, y, z, w = (finite(x) for x in event['quaternion'])
            relative = Quaternion((w, x, y, z))
            if relative.magnitude > 0.01:
                relative.normalize()
                basis = Quaternion((1, 0, 0), math.pi / 2)
                camera = self.local_camera()
                camera.rotation_mode = 'QUATERNION'
                camera.rotation_quaternion = (basis @ relative @ basis.inverted() @ self.sensor_base).normalized()
        elif kind in ('play', 'record'):
            if self.recording:
                return
            if self.scene.frame_current >= self.scene.frame_end:
                self.scene.frame_set(self.scene.frame_start)
            if kind == 'record':
                self.control_hold = False
                original = self.camera()
                matrix = original.matrix_world.copy()
                camera = original.copy()
                camera.data = original.data.copy()
                camera.animation_data_clear()
                camera.data.animation_data_clear()
                camera.parent = None
                camera.constraints.clear()
                camera.name = 'Camera_Take_' + time.strftime('%H%M%S')
                camera.rotation_mode = 'QUATERNION'
                camera.matrix_world = matrix
                self.scene.collection.objects.link(camera)
                self.scene.camera = camera
                self.take_name = camera.name
                self.scene['previs_last_take'] = camera.name
                self.take_start = self.scene.frame_current
                self.take_end = self.take_start
                self.last_record_frame = -1
                self.last_record_quaternion = None
                self.take_first_pose = None
                camera['previs_take_motion'] = False
                camera['previs_created_at'] = time.time()
                self.recording = True
                self.record_key()
                self.export_state = {'status': 'idle'}
            elif self.recorded_take_info(self.camera().name):
                self.control_hold = True
            self.start_frame = self.scene.frame_current
            self.play_started = time.monotonic()
            self.playing = True
        elif kind in ('pause', 'stop'):
            if self.recording:
                self.record_key()
                self.linearize_take()
                self.control_hold = True
            self.recording = False
            self.playing = False
            self.move = Vector((0, 0, 0))
        elif kind == 'seek' and not self.recording:
            self.playing = False
            self.scene.frame_set(int(finite(event.get('frame'), self.scene.frame_start,
                                             self.scene.frame_start, self.scene.frame_end)))
            if self.recorded_take_info(self.camera().name):
                self.control_hold = True
        elif kind == 'camera' and not self.recording:
            camera = self.scene.objects.get(event.get('name', ''))
            if camera and camera.type == 'CAMERA':
                self.scene.camera = camera
                self.sensor_base = None
                self.control_hold = bool(self.recorded_take_info(camera.name))
        elif kind == 'reset_camera' and not self.recording:
            camera = self.local_camera()
            reset = self.camera_resets.get(camera.name)
            if reset:
                camera.matrix_world = reset.copy()
            self.sensor_base = None
        elif kind == 'settings':
            if 'speed' in event:
                self.speed = finite(event['speed'], 1.5, 0.1, 10)
            if 'lens' in event:
                self.local_camera().data.lens = finite(event['lens'], 35, 12, 150)
        elif kind == 'export':
            self.begin_export(event.get('camera'), event.get('mode', 'pov'), event.get('simplify', True))
        elif kind.startswith('brief_'):
            if kind=='brief_create':
                source=event.get('source')
                if source:self.projects.entry(source)
                self.briefs.create(event)
            elif kind=='brief_reply':self.briefs.reply(event)
            else:
                pid=event.get('project_id')
                if pid:self.projects.entry(pid)
                if event.get('status')=='ready':
                    pid=pid or self.briefs.find(event.get('id')).get('project_id')
                    if not pid or not self.projects.path(pid).is_file():raise ValueError('请先保存制作好的项目')
                self.briefs.update(event)
            self.error=''
        elif kind.startswith('project_'):
            if self.recording or self.export_process:raise ValueError('请先停止录制并等待导出完成，再切换或保存项目')
            manager=self.projects
            self.playing=False;self.move=Vector((0,0,0));self.sensor_base=None;self.control_hold=True
            self.dispose_overview()
            if kind=='project_save':
                manager.write_scene(self.scene,manager.catalog['active']);message='当前项目已保存'
            elif kind=='project_update':
                pid=event.get('id',manager.catalog['active']);manager.metadata(pid,event.get('name',''),event.get('description',''))
                target=manager.load(pid);p=manager.entry(pid);target['previs_title']=p['name'];target['previs_subtitle']=p['description'];manager.write_scene(target,pid);message='项目名称与场景描述已保存'
            else:
                manager.write_scene(self.scene,manager.catalog['active'])
                if kind=='project_create':
                    pid,target=manager.create(self.scene,event.get('name',''),event.get('description',''),event.get('source','current'))
                else:
                    pid=event.get('id');target=manager.load(pid)
                if target.camera is None:raise ValueError('目标场景没有摄影机，请在 Blender 中添加后再切换')
                self.window.scene=target;self.window.view_layer.update()
                manager.catalog['active']=pid;manager.persist()
                self.take_name=target.get('previs_last_take','');self.camera_resets={};self.last_record_frame=-1;self.last_record_quaternion=None
                self.frame_bytes=b'';self.export_state={'status':'idle'};self.downloads=set();self.events.clear()
                message='已切换到 '+manager.entry(pid)['name']
            self.project_event+=1;self.project_message=message;self.error=''
        elif kind == 'zones':
            if self.recording:
                raise ValueError('请先停止录制，再修改空间分区')
            if self.export_process:
                raise ValueError('请等当前导出完成，再修改空间分区')
            module = overview_module()
            zones = module.validate_zones(event.get('zones'))
            previous = self.scene.get('previs_zones')
            previous_revision = int(self.scene.get('previs_zones_revision', 0))
            self.dispose_overview()
            module.write_zones(self.scene, zones)
            self.scene['previs_zones_revision'] = previous_revision + 1
            try:
                if getattr(self,'projects',None):self.projects.write_scene(self.scene,self.projects.catalog['active'])
                else:
                    destination = bpy.data.filepath or str(ROOT / 'projects/当前拍摄.blend')
                    bpy.ops.wm.save_as_mainfile(filepath=destination)
            except Exception:
                if previous is None:
                    del self.scene['previs_zones']
                else:
                    self.scene['previs_zones'] = previous
                self.scene['previs_zones_revision'] = previous_revision
                raise
            self.error = ''

    def tick(self):
        if self.closed:
            return None
        now = time.monotonic()
        dt = min(now - self.last_tick, 0.1)
        self.last_tick = now
        try:
            if self.area not in self.window.screen.areas[:] or self.area.type != 'VIEW_3D':
                area = next((a for a in self.window.screen.areas if a.type == 'VIEW_3D'), None)
                if area is None:
                    self.error = '请让 Blender 保留一个可见的 3D 视图'
                    self.refresh_state()
                    return 0.2
                self.area = area
                self.region = next(r for r in area.regions if r.type == 'WINDOW')
                self.space = area.spaces.active
            # Remember the live transform before advancing scene animation evaluates its action.
            live_matrix = self.camera().matrix_world.copy() if self.recording else None
            while self.events:
                self.process(self.events.popleft())
                self.window.view_layer.update()
            if self.playing:
                fps = self.scene.render.fps / self.scene.render.fps_base
                frame = min(self.scene.frame_end, self.start_frame + int((now - self.play_started) * fps))
                if self.recording:
                    live_matrix = self.camera().matrix_world.copy()
                selected_camera = self.camera()
                pinned_camera = self.recording or bool(self.recorded_take_info(selected_camera.name))
                self.scene.frame_set(frame)
                if pinned_camera:
                    self.scene.camera = selected_camera
                if self.recording and live_matrix is not None:
                    self.camera().matrix_world = live_matrix
            if now - self.last_input > 0.35:
                self.move = Vector((0, 0, 0))
            if self.move.length_squared:
                camera = self.local_camera()
                q = camera.matrix_world.to_quaternion()
                right = q @ Vector((1, 0, 0))
                forward = q @ Vector((0, 0, -1))
                # Planar motion stays level; dedicated up/down controls elevation.
                right.z = 0; forward.z = 0
                if right.length: right.normalize()
                if forward.length: forward.normalize()
                delta = right * self.move.x + forward * self.move.y + Vector((0, 0, self.move.z))
                if delta.length > 1: delta.normalize()
                camera.location += delta * self.speed * dt
            if self.recording:
                self.record_key()
            if self.playing and self.scene.frame_current >= self.scene.frame_end:
                self.process({'type': 'stop'})
            if self.export_process and self.export_process.poll() is not None:
                self.finish_export()
            self.prepare_overview()
            self.refresh_state()
            self.area.tag_redraw()
        except Exception as error:
            self.error = str(error)
            self.refresh_state()
        return 1 / 30

    def draw(self):
        now = time.monotonic()
        if self.closed or self.capture_busy or now - self.last_draw < 0.12:
            return
        if bpy.context.area != self.area or bpy.context.region != self.region or not self.scene.camera:
            return
        self.capture_busy = True
        try:
            if self.offscreen is None:
                self.offscreen = gpu.types.GPUOffScreen(WIDTH, HEIGHT)
            camera = self.scene.camera
            matrix = camera.calc_matrix_camera(self.scene.evaluated_depsgraph_get() if hasattr(self.scene, 'evaluated_depsgraph_get')
                                              else bpy.context.evaluated_depsgraph_get(), x=WIDTH, y=HEIGHT)
            with self.offscreen.bind():
                self.offscreen.draw_view3d(self.scene, self.window.view_layer, self.space, self.region,
                                          camera.matrix_world.inverted(), matrix, do_color_management=True)
                buffer = gpu.state.active_framebuffer_get().read_color(0, 0, WIDTH, HEIGHT, 4, 0, 'UBYTE')
                self.frame_bytes = png_rgba(buffer, WIDTH, HEIGHT)
            self.stream_fps = round(1 / max(0.001, now - self.last_draw), 1) if self.last_draw else 0
            self.last_draw = now
            self.draw_overview()
            if self.error.startswith(('取景输出：', '请让 Blender 保留')):
                self.error = ''
        except Exception as error:
            self.error = '取景输出：' + str(error)
            self.last_draw = now
            if self.offscreen is not None:
                try:
                    self.offscreen.free()
                except Exception:
                    pass
                self.offscreen = None
        finally:
            self.capture_busy = False

    def dispose_overview(self):
        rig = getattr(self, 'overview_rig', None)
        if rig:
            rig.close()
        self.overview_rig = None
        self.overview_bytes = b''
        self.overview_frame = None

    def prepare_overview(self):
        # Scene edits and dependency evaluation must run outside the GPU draw
        # callback. Changing context there can deadlock Blender's draw manager.
        try:
            module = overview_module()
            signature = (json.dumps(module.read_zones(self.scene), sort_keys=True),
                         tuple(sorted(o.name for o in self.scene.objects if not o.hide_render)))
            if self.overview_rig is None or signature != getattr(self, 'overview_signature', None):
                self.dispose_overview()
                self.overview_rig = module.OverviewRig(self.scene)
                self.overview_signature = signature
            self.overview_rig.update(self.scene.camera, self.scene.frame_current)
            self.overview_error = ''
        except Exception as error:
            self.overview_error = '空间总览：' + str(error)

    def draw_overview(self):
        rig = self.overview_rig
        if rig is None or time.monotonic()-getattr(self,'last_overview_capture',0)<.3:
            return
        self.last_overview_capture=time.monotonic()
        width,height=1280,720
        try:
            view_layer = rig.scene.view_layers[0]
            camera = rig.scene.camera
            matrix = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(), x=width, y=height)
            if self.overview_offscreen is None:
                self.overview_offscreen = gpu.types.GPUOffScreen(width, height)
            shading = self.space.shading
            old_background, old_color = shading.background_type, tuple(shading.background_color)
            try:
                shading.background_type = 'VIEWPORT'
                shading.background_color = (.83, .85, .81)
                with self.overview_offscreen.bind():
                    self.overview_offscreen.draw_view3d(rig.scene, view_layer, self.space, self.region,
                        camera.matrix_world.inverted(), matrix, do_color_management=True)
                    buffer = gpu.state.active_framebuffer_get().read_color(0, 0, width, height, 4, 0, 'UBYTE')
                    self.overview_bytes = png_rgba(buffer, width, height)
            finally:
                shading.background_type = old_background
                shading.background_color = old_color
            self.overview_frame = self.scene.frame_current
            self.overview_error = ''
        except Exception as error:
            self.overview_error = '空间总览：' + str(error)

    def overview_state(self):
        try:
            zones=overview_module().read_zones(self.scene)
            p=self.scene.camera.matrix_world.translation if self.scene.camera else Vector((0,0,0))
            active=next((z['id'] for z in zones if abs(p.x-z['x'])<=z['width']/2 and abs(p.y-z['y'])<=z['depth']/2),'')
            return {'zones': zones,'active_zone':active,'meters_per_unit': self.scene.unit_settings.scale_length,
                    'revision': int(self.scene.get('previs_zones_revision', 0)),
                    'frame': getattr(self, 'overview_frame', None),
                    'ready': bool(getattr(self, 'overview_bytes', b'')),
                    'error': getattr(self, 'overview_error', '')}
        except Exception as error:
            return {'zones': [], 'revision': 0, 'ready': False, 'error': str(error)}

    def begin_export(self, camera_name=None, mode='pov', simplify=True):
        if self.recording or self.export_process:
            return
        take = self.recorded_take_info(camera_name)
        if take is None or take['frames'] < 2:
            self.export_state = {'status': 'error', 'message': '还没有录好的镜头。请点击“开始录制”，运镜后停止，再导出。'}
            return
        if mode not in ('pov', 'overview', 'spatial'):
            self.export_state = {'status': 'error', 'message': '未知导出类型'}
            return
        self.playing = False
        name = 'whitebox_' + time.strftime('%Y%m%d_%H%M%S')
        snapshot = TAKES / (name + '.blend')
        output = TAKES / (name + '.mp4')
        start, end = take['start'], take['end']
        export_camera = self.scene.objects[take['name']]
        if mode in ('overview','spatial'):
            module = overview_module()
            module.write_zones(self.scene, module.read_zones(self.scene))
        self.dispose_overview()
        # Save a render copy. The user's active .blend name remains unchanged.
        current_camera = self.scene.camera
        try:
            self.scene.camera = export_camera
            bpy.data.libraries.write(str(snapshot),{self.scene},path_remap='ABSOLUTE',fake_user=True,compress=True)
        finally:
            self.scene.camera = current_camera
        self.export_log = (TAKES / (name + '.log')).open('w')
        self.export_name = output.name
        self.export_camera_name = export_camera.name
        self.export_mode = mode
        self.export_process = subprocess.Popen([bpy.app.binary_path, '--background', '--factory-startup', str(snapshot),
            '--python-exit-code', '1', '--python', str(ROOT / 'scripts/render_take.py'), '--', str(output), str(start), str(end), export_camera.name, mode, 'simple' if simplify else 'full'],
            stdout=self.export_log, stderr=subprocess.STDOUT)
        self.export_state = {'status': 'running', 'message': ({'overview':'正在导出参考套件 ','spatial':'正在单独导出空间 16:9 ','pov':'正在导出镜头 16:9 '}[mode]) + export_camera.name,
                             'camera': export_camera.name}

    def finish_export(self):
        try:
            if self.export_log:
                self.export_log.close()
                self.export_log = None
            file = TAKES / self.export_name
            mode=getattr(self,'export_mode','pov')
            if self.export_process.returncode != 0:raise ValueError('导出失败，请查看 takes 内的渲染日志')
            specs=[] if mode=='spatial' else [('.mp4','镜头 · 16:9 · 1280×720')]
            if mode in ('overview','spatial'):
                specs += [('_board.mp4','空间说明 · 16:9 · 1920×1080'),('_overview.mp4','纯俯视 · 16:9 · 1280×720')]
                if mode=='overview':specs.append(('_combined.mp4','上下组合 · 两块各 16:9'))
                specs += [('_zones.json','空间数据 JSON'),('_reference.txt','AI 参考说明 TXT'),('_board.png','空间说明图 · 16:9')]
            files=[]
            for suffix,label in specs:
                artifact=TAKES/(file.stem+suffix)
                if not artifact.exists() or not artifact.stat().st_size:raise ValueError('导出缺少文件：'+artifact.name)
                files.append({'label':label,'name':artifact.name})
            for artifact in files:
                self.downloads.add(artifact['name'])
                artifact['url'] = '/download/' + artifact.pop('name') + '?token=' + self.token
            primary = next((f for f in files if '_combined.mp4' in f['url']),files[0])
            self.export_state = {'status': 'done', 'url': primary['url'], 'files': files,
                                 'message': file.name, 'camera': self.export_camera_name}
        except Exception as error:
            self.export_state = {'status': 'error', 'message': str(error)}
        finally:
            self.export_process = None

    def refresh_state(self):
        camera = self.scene.camera
        take = self.recorded_take_info(camera.name) if camera else None
        take = take or self.recorded_take_info()
        self.state = {'ok': True, 'connected': not self.closed,
            'camera': camera.name if camera else '', 'cameras': [o.name for o in self.scene.objects if o.type == 'CAMERA'],
            'frame': self.scene.frame_current, 'frame_start': self.scene.frame_start, 'frame_end': self.scene.frame_end,
            'fps': self.scene.render.fps / self.scene.render.fps_base, 'playing': self.playing, 'recording': self.recording,
            'take_name': self.take_name, 'speed': self.speed, 'lens': camera.data.lens if camera else 35,
            'recorded_take': take, 'record_status': 'recording' if self.recording else ('ready' if take else 'idle'),
            'control_hold': getattr(self, 'control_hold', False),
            'stream_fps': self.stream_fps, 'error': self.error, 'export': self.export_state,
            'overview': self.overview_state(),
            'projects':self.projects.public() if getattr(self,'projects',None) else {'active':None,'items':[]},
            'briefs':self.briefs.data if getattr(self,'briefs',None) else {'revision':0,'items':[]},
            'project_event':getattr(self,'project_event',0),'project_message':getattr(self,'project_message',''),
            'scene_title': str(self.scene.get('previs_title','空间与镜头，一起预演。')),
            'scene_subtitle': str(self.scene.get('previs_subtitle','同一时间轴上的空间总览与真实取景。')),
            'story': json.loads(self.scene.get('previs_story','[]')),
            'subjects': json.loads(self.scene.get('previs_subjects','[]')),
            'http_url': self.http_url, 'https_url': self.https_url}

    def close(self):
        self.closed = True
        if self.recording:
            self.process({'type': 'stop'})
        if bpy.app.timers.is_registered(self.tick):
            bpy.app.timers.unregister(self.tick)
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        for server in self.servers:
            threading.Thread(target=lambda s=server: (s.shutdown(), s.server_close()), daemon=True).start()
        if self.offscreen:
            self.offscreen.free()
        if self.overview_offscreen:
            self.overview_offscreen.free()
        self.dispose_overview()

class WBVCAM_OT_start(bpy.types.Operator):
    bl_idname = 'wbvcam.start'
    bl_label = '启动手机网页'
    def execute(self, context):
        global SERVICE
        if SERVICE:
            return {'FINISHED'}
        try:
            SERVICE = Viewfinder(context)
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}

class WBVCAM_OT_stop(bpy.types.Operator):
    bl_idname = 'wbvcam.stop'
    bl_label = '停止网页连接'
    def execute(self, context):
        global SERVICE
        if SERVICE:
            SERVICE.close()
            SERVICE = None
        return {'FINISHED'}

class WBVCAM_OT_open(bpy.types.Operator):
    bl_idname = 'wbvcam.open'
    bl_label = '在电脑打开取景器'
    def execute(self, context):
        if SERVICE:
            bpy.ops.wm.url_open(url=SERVICE.http_url.replace(SERVICE.ip, '127.0.0.1'))
        return {'FINISHED'}

class WBVCAM_PT_panel(bpy.types.Panel):
    bl_label = 'DKYJ Director · 导演台'
    bl_idname = 'WBVCAM_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '网页摄影机'
    def draw(self, context):
        layout = self.layout
        if not SERVICE:
            layout.operator('wbvcam.start', icon='PLAY')
            layout.label(text='同一 Wi-Fi，手机 Safari 打开链接')
            return
        layout.label(text='局域网取景器已启动', icon='CHECKMARK')
        layout.label(text=f'{SERVICE.ip}:8765')
        layout.operator('wbvcam.open', icon='URL')
        layout.operator('wbvcam.stop', icon='PAUSE')
        layout.separator()
        layout.label(text=f'取景 {SERVICE.stream_fps:.1f} fps')
        layout.label(text='录制中' if SERVICE.recording else '触控移动 / 体感转向')
        if SERVICE.error:
            layout.label(text=SERVICE.error[:38], icon='ERROR')

CLASSES = (WBVCAM_OT_start, WBVCAM_OT_stop, WBVCAM_OT_open, WBVCAM_PT_panel)

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    global SERVICE
    if SERVICE:
        SERVICE.close()
        SERVICE = None
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
