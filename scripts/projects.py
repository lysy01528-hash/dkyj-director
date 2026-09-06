"""Data-only CLI for local agents and project management."""
import argparse,json,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('action',choices=['list','save','switch','create','update']);p.add_argument('--id');p.add_argument('--name');p.add_argument('--description',default='');p.add_argument('--source',default='current');a=p.parse_args()
info=json.loads((root/'runtime/connection.json').read_text(encoding='utf-8'));base='http://127.0.0.1:8765';token=info['token'];opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path,data=None):
    body=None if data is None else json.dumps(data).encode()
    req=urllib.request.Request(base+path+'?token='+token,data=body,headers={'Content-Type':'application/json'})
    return json.load(opener.open(req,timeout=15))
s=request('/api/state')
if a.action!='list':
    event=s.get('project_event',0);body={'type':'project_'+a.action,'description':a.description,'source':a.source}
    if a.id:body['id']=a.id
    if a.name:body['name']=a.name
    response=request('/api/control',body)
    if response.get('ok') is False:raise SystemExit(response.get('error'))
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        time.sleep(.4);s=request('/api/state')
        if s.get('error'):raise SystemExit(s['error'])
        if s.get('project_event',0)>event:break
    else:raise SystemExit('操作尚未确认，请检查网页状态；不要重复创建项目。')
print(json.dumps(s.get('projects',{}),ensure_ascii=False,indent=2))
