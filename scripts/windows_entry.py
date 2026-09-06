"""Double-click Windows setup/launch entry, without PowerShell policy changes."""
import os
from pathlib import Path
import subprocess
import sys


def main():
    if sys.version_info < (3, 11):
        raise SystemExit('Python 3.11+ required: https://www.python.org/downloads/windows/')
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    python = root/'.venv/Scripts/python.exe'
    install = len(sys.argv) > 1 and sys.argv[1] == 'install'
    if install or not all(p.exists() for p in [python, root/'examples/steamship_scene.blend', root/'runtime/setup.json']):
        subprocess.run([sys.executable, str(root/'scripts/setup.py')], check=True)
    if install:
        print('Installed. Next: double-click Launch DKYJ Director.cmd. Phone: iPhone Safari.')
    else:
        subprocess.run([str(python), str(root/'scripts/launch.py')], check=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit('DKYJ did not finish: ' + str(error) + '\nSee docs/windows.md.')
