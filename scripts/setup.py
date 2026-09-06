"""Install local dependencies and create bundled scenes once."""
import argparse,json,os,subprocess,venv
from pathlib import Path
from platform_paths import blender_binary,project_python
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--blender');args=p.parse_args()
if args.blender:os.environ['DKYJ_BLENDER']=args.blender
try:
    binary=blender_binary()
except RuntimeError as error:
    raise SystemExit(str(error))
python=project_python(root)
if not python.exists():venv.EnvBuilder(with_pip=True).create(root/'.venv')
subprocess.run([str(python),'-m','pip','install','-r',str(root/'requirements.txt')],check=True)
for scene,script in [('steamship_scene','create_steamship_scene'),('calibration_scene','create_calibration_scene')]:
    if not (root/'examples'/f'{scene}.blend').exists():
        (root/'examples').mkdir(exist_ok=True)
        subprocess.run([binary,'--background','--factory-startup','--python-exit-code','1','--python',str(root/'scripts'/f'{script}.py')],check=True)
subprocess.run([binary,'--background','--factory-startup','--python-exit-code','1','--python',str(root/'scripts/install_webcam.py')],check=True)
(root/'runtime').mkdir(exist_ok=True)
(root/'runtime/setup.json').write_text(json.dumps({'blender':str(Path(binary).resolve())}),encoding='utf-8')
print('DKYJ Director 已就绪。运行：'+str(python)+' scripts/launch.py')
