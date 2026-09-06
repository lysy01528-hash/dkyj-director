"""Read-only local setup checks. Never prints tokens, keys, or scene content."""
import importlib.util,json,socket,subprocess,sys,urllib.request
from pathlib import Path
from platform_paths import blender_binary,project_python

def main():
    root=Path(__file__).resolve().parents[1];report={}
    try:blender_binary();report['blender']='found'
    except RuntimeError:report['blender']='missing; install Blender or set DKYJ_BLENDER'
    python=project_python(root)
    if python.exists():
        check=subprocess.run([str(python),'-c','import cryptography,PIL,qrcode'],capture_output=True)
        report['python_dependencies']='ready' if check.returncode==0 else 'incomplete; run setup.py'
    else:report['python_dependencies']='missing; run setup.py'
    report['director']='not connected; start launch.py'
    try:
        info=json.loads((root/'runtime/connection.json').read_text(encoding='utf-8'))
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open('http://127.0.0.1:8765/api/state?token='+info['token'],timeout=3) as response:state=json.load(response)
        if state.get('connected'):report['director']='connected';report['projects']=len(state.get('projects',{}).get('items',[]))
    except (OSError,ValueError,KeyError):pass
    try:
        with socket.create_connection(('127.0.0.1',9876),timeout=2):report['mcp_socket']='listening; verify scene inspection in your agent'
    except OSError:report['mcp_socket']='not listening; optional for manual use'
    report['hosting']='local computer; GitHub Pages cannot run the Blender backend'
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['director']=='connected' else 1

if __name__=='__main__':sys.exit(main())
