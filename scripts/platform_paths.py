"""Runtime paths discovered on the user's macOS or Windows computer."""
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version_key(path):
    return tuple(int(x) for x in re.findall(r'\d+', path.parent.name))


def blender_binary():
    configured = os.environ.get('DKYJ_BLENDER')
    saved = ROOT / 'runtime/setup.json'
    stored = json.loads(saved.read_text(encoding='utf-8')).get('blender') if saved.exists() else None
    if configured:
        if not Path(configured).is_file():
            raise RuntimeError('DKYJ_BLENDER does not point to a Blender executable: ' + configured)
        return configured
    candidates = [stored, shutil.which('blender')]
    if sys.platform == 'win32':
        folders = [Path(os.environ.get(key, default)) for key, default in
                   [('PROGRAMFILES', 'C:/Program Files'), ('LOCALAPPDATA', str(Path.home()/'AppData/Local'))]]
        found = [p for folder in folders for p in folder.glob('Blender Foundation/Blender */blender.exe')]
        candidates.extend(str(p) for p in sorted(found, key=version_key, reverse=True))
    else:
        candidates.append('/Applications/Blender.app/Contents/MacOS/Blender')
    for path in candidates:
        if path and Path(path).is_file():
            return str(path)
    raise RuntimeError('Blender not found. Download https://www.blender.org/download/ or pass --blender / set DKYJ_BLENDER to its executable path.')


def project_python(root):
    return Path(root)/'.venv'/('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')


def chinese_font():
    windows_fonts = Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'
    candidates = [os.environ.get('DKYJ_FONT', ''), '/System/Library/Fonts/PingFang.ttc',
                  '/System/Library/Fonts/STHeiti Medium.ttc', str(windows_fonts/'msyh.ttc'),
                  str(windows_fonts/'msyh.ttf'), str(windows_fonts/'simhei.ttf'), str(windows_fonts/'simsun.ttc')]
    for path in candidates:
        if path and Path(path).is_file():
            return path
    raise RuntimeError('Chinese font missing. Install Microsoft YaHei / Chinese supplemental fonts or set DKYJ_FONT to a CJK .ttf/.ttc file. See docs/windows.md.')
