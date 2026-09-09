"""Create an allowlisted source distribution, never copy working projects or credentials."""
import argparse,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];VERSION='0.7.0-preview.5';name='dkyj-director-'+VERSION
files=['tests/test_deleted_data.py','tests/test_overview_lifecycle.py','scripts/test_live_deletion.py','docs/fixes/deleted-camera-recovery.md','samples/README.md','samples/room-pov.mp4','samples/room-overview.mp4','samples/steamship-pov.mp4','samples/steamship-overview.mp4','samples/room-preview.jpg','docs/release-notes.md','scripts/network_utils.py','scripts/windows_entry.py','tests/test_platform.py','docs/windows.md','Install DKYJ Director.cmd','Launch DKYJ Director.cmd','docs/release-check.md','.github/assets/dkyj-director-hand-eye.png','tests/test_export_files.py','docs/export-formats.md','docs/logo-generation.md','addon/scene_briefs.py','web/welcome.js','scripts/agent_server.py','scripts/director_client.py','scripts/agent_config.py','requirements-agent.txt','tests/test_briefs.py','docs/trial-guide.md','README.zh-CN.md','AGENT_GUIDE.md','Launch DKYJ Director.command','docs/agent-setup.md','docs/github-publishing.md','scripts/doctor.py','README.md','LICENSE','CHANGELOG.md','.gitignore','requirements.txt','打开大开眼界导演台.command',
'addon/whitebox_webcam.py','addon/whitebox_overview.py','addon/scene_projects.py',
'web/index.html','web/app.css','web/app.js','web/overview.js','web/projects.js',
'scripts/setup.py','scripts/platform_paths.py','scripts/launch.py','scripts/start_session.py','scripts/install_webcam.py','scripts/create_local_tls.py','scripts/create_steamship_scene.py','scripts/create_calibration_scene.py','scripts/render_take.py','scripts/compose_overview.py','scripts/projects.py','scripts/package_release.py','scripts/test_recorded_export.py','scripts/test_web_controls.cjs',
 'tests/test_projects.py','docs/project-api.md','docs/architecture.md','docs/development-log.md','docs/seedance-2.5-reference.md','.github/workflows/ci.yml','.github/assets/steamship-board.png']
parser=argparse.ArgumentParser()
parser.add_argument('--platform', choices=['all','macos','windows'], default='all')
args=parser.parse_args()
launchers={'macos':['Launch DKYJ Director.command','打开大开眼界导演台.command'],
           'windows':['Install DKYJ Director.cmd','Launch DKYJ Director.cmd']}
# A platform ZIP can rebuild itself; the full repository can rebuild both.
optional=set(sum(launchers.values(),[]))
files=[f for f in files if f not in optional or (ROOT/f).exists()]
dist=ROOT/'dist';dist.mkdir(exist_ok=True)

def prepare(target, chosen):
    if target.exists():shutil.rmtree(target)
    target.mkdir()
    for f in chosen:
        src=ROOT/f
        if src.is_symlink():raise RuntimeError('Symlink rejected: '+f)
        if any(part in {'projects','takes','qa','runtime','vendor','.venv'} for part in Path(f).parts):raise RuntimeError('Private directory rejected: '+f)
        if src.suffix not in {'.png','.jpg','.mp4'}:
            text=src.read_text(encoding='utf-8')
            forbidden=[str(ROOT),str(Path.home()),'-----BEGIN '+ 'PRIVATE KEY-----']
            connection=ROOT/'runtime/connection.json'
            if connection.exists():
                token=json.loads(connection.read_text(encoding='utf-8')).get('token')
                if token:forbidden.append(token)
            if any(word in text for word in forbidden):raise RuntimeError('Private data found in '+f)
        dest=target/f;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        if dest.suffix==".command":dest.chmod(0o755)

def manifest(target):
    data={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()
          for f in target.rglob('*') if f.is_file() and f.name!='MANIFEST.sha256.json'}
    (target/'MANIFEST.sha256.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

source=dist/name
prepare(source,files);manifest(source)
outputs=[]
for platform in (['macos','windows'] if args.platform=='all' else [args.platform]):
    if not all((ROOT/f).exists() for f in launchers[platform]):
        raise SystemExit('Missing '+platform+' launchers. Rebuild this ZIP with --platform '+('macos' if platform=='windows' else 'windows')+' or use the full source repository.')
    chosen=[f for f in files if f not in optional or f in launchers[platform]]
    target=dist/(name+'-'+platform);prepare(target,chosen)
    intro=('# DKYJ Director — '+platform+'\n\n'+
           ('Install Blender + Python, then open Launch DKYJ Director.command.\n\n安装 Blender、Python 后双击 Launch DKYJ Director.command。电脑 Safari。\n' if platform=='macos' else
            'Install Blender + Python, then run Install DKYJ Director.cmd, followed by Launch DKYJ Director.cmd.\n\n先安装 Blender、Python，再双击 Install DKYJ Director.cmd，之后双击 Launch DKYJ Director.cmd。电脑 Edge。详见 docs/windows.md。Windows 真机渲染尚待验证。\n')+
           '\n手机端仅支持 iPhone Safari / Phone: iPhone Safari only.\n\nFull guide: README.md / README.zh-CN.md.\n')
    (target/'START_HERE.md').write_text(intro,encoding='utf-8');manifest(target)
    archive=dist/(target.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(target.rglob('*')):
            if file.is_file():z.write(file,target.name+'/'+file.relative_to(target).as_posix())
    checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
    (dist/(target.name+'.sha256')).write_text(checksum+'  '+archive.name+'\n',encoding='utf-8')
    outputs.append({'platform':platform,'zip':str(archive),'bytes':archive.stat().st_size,'sha256':checksum})
print(json.dumps({'source_directory':str(source),'packages':outputs},ensure_ascii=False,indent=2))
