"""Authenticated local director client; credentials stay on this machine."""
import json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def request(path,data=None):
    token=json.loads((ROOT/'runtime/connection.json').read_text(encoding='utf-8'))['token']
    req=urllib.request.Request('http://127.0.0.1:8765'+path+'?token='+token,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=15) as r:return json.load(r)
def state():return request('/api/state')
def command(body):
    before=state();project=body['type'].startswith('project_');revision=before.get('project_event',0) if project else before.get('briefs',{}).get('revision',0)
    request('/api/control',body);deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        time.sleep(.25);s=state();now=s.get('project_event',0) if project else s.get('briefs',{}).get('revision',0)
        if now>revision:return s
        # Retry of a client-generated brief id is idempotent.
        if body['type']=='brief_create' and any(b['id']==body['id'] for b in s.get('briefs',{}).get('items',[])):return s
        if s.get('error') and s['error']!=before.get('error'):raise RuntimeError(s['error'])
    raise TimeoutError('Command not confirmed; inspect director state before retrying.')
