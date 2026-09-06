"""Open the existing viewfinder or launch one dedicated Blender window and prepare pairing."""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path
import qrcode
from platform_paths import blender_binary
root = Path(__file__).resolve().parents[1]
connection = root / 'runtime/connection.json'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def active_connection():
    try:
        info = json.loads(connection.read_text(encoding='utf-8'))
        url = 'http://127.0.0.1:8765/api/state?token=' + info['token']
        state = json.load(opener.open(url, timeout=1))
        return info if state.get('connected') else None
    except (OSError, ValueError):
        return None

def pairing(info):
    qrcode.make(info['http_url']).save(root / 'runtime/phone-pairing.png')
    print('\n手机与电脑连接同一 Wi-Fi，用 Safari 打开：\n' + info['http_url'])
    print('体感 HTTPS：\n' + (info['https_url'] or '暂未启用'))
    print('请先通过 HTTP 试触控；体感需在 iPhone 安装并信任项目本地证书。')
    print('二维码：' + str(root / 'runtime/phone-pairing.png'))

info = active_connection()
if not info:
    subprocess.run([sys.executable, str(root / 'scripts/create_local_tls.py')], check=True)
    (root/'qa').mkdir(exist_ok=True)
    log = (root / 'qa/blender-session.log').open('a')
    working_scene = root / 'projects/当前拍摄.blend'
    scene_file = working_scene if working_scene.exists() else root / 'examples/steamship_scene.blend'
    catalog=root/'projects/index.json'
    if catalog.exists():
        data=json.loads(catalog.read_text(encoding='utf-8'));active=data.get('active','')
        import re
        if isinstance(active,str) and re.fullmatch(r'[a-z0-9-]{1,64}',active):
            saved=root/'projects/library'/active/'scene.blend'
            if saved.is_file():scene_file=saved
    if not scene_file.exists():raise SystemExit('请先运行 python3 scripts/setup.py 初始化示例场景。')
    process = subprocess.Popen([
        blender_binary(), str(scene_file),
        '--python', str(root / 'scripts/start_session.py')],
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
        env={**os.environ, 'BLENDER_MCP_DISABLE_TELEMETRY':'1', 'PREVIS_RESUME': '1'})
    for _ in range(150):
        if process.poll() is not None:
            raise SystemExit('Blender 未能启动，请查看 qa/blender-session.log')
        info = active_connection()
        if info:
            break
        time.sleep(.2)
    if not info:
        raise SystemExit('Blender 仍在启动；保持窗口打开，稍后再次双击启动器即可。')
pairing(info)
if sys.platform == 'win32':
    print('Windows: allow Blender on Private networks if the firewall asks. Phone: iPhone Safari only.')
if info.get('http_url', '').startswith('http://127.0.0.1:'):
    print('No LAN address found. Join Wi-Fi or set DKYJ_LAN_IP to this computer’s private IPv4 address, then restart Blender.')
if '--no-browser' not in sys.argv:
    desktop_url = 'http://127.0.0.1:8765/?token=' + info['token']
    if sys.platform == 'darwin':
        result = subprocess.run(['open', '-a', 'Safari', desktop_url], capture_output=True)
        if result.returncode:
            print('Safari 未能自动打开，请在 Safari 中手动打开：' + desktop_url)
    elif sys.platform == 'win32':
        edge = shutil.which('msedge')
        for folder in [os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)'), os.environ.get('PROGRAMFILES', 'C:/Program Files'), os.environ.get('LOCALAPPDATA', '')]:
            candidate = Path(folder)/'Microsoft/Edge/Application/msedge.exe'
            if candidate.is_file():
                edge = str(candidate)
                break
        if edge:
            subprocess.Popen([edge, desktop_url])
        else:
            print('Edge not found; opening the default desktop browser. Phone support: iPhone Safari only.')
            webbrowser.open(desktop_url)
    else:
        webbrowser.open(desktop_url)
