(()=>{
const $=id=>document.getElementById(id), dialog=$('projectDialog');let catalog={items:[]},editing=null,pending=null,event=0,signature='';
const feedback=t=>$('projectFeedback').textContent=t;
function reset(){editing=null;$('projectForm').reset();$('projectFormTitle').textContent='另存为新项目';$('projectSourceLabel').hidden=false;$('projectSubmit').textContent='创建并打开';$('projectNew').hidden=true;}
function send(body){if(pending!==null)return;pending=event;feedback('正在保存和载入，请稍候…');window.previsControl(body);}
$('projectsBtn').onclick=()=>{window.dispatchEvent(new CustomEvent('previs-overview-editing',{detail:true}));dialog.showModal();};
$('projectClose').onclick=()=>dialog.close();dialog.addEventListener('close',()=>window.dispatchEvent(new CustomEvent('previs-overview-editing',{detail:false})));
$('projectNew').onclick=reset;$('projectSave').onclick=()=>send({type:'project_save'});
$('projectForm').onsubmit=e=>{e.preventDefault();send({type:editing?'project_update':'project_create',...(editing?{id:editing}:{}),name:$('projectName').value,description:$('projectDescription').value,source:$('projectSource').value});};
window.previsProjects={render(s){const zoneLocked=window.previsOverview?.canSwitchProject?.()===false;$('projectsBtn').disabled=zoneLocked;$('projectsBtn').title=zoneLocked?'请先保存空间编辑':'打开场景项目库';event=s.project_event||0;catalog=s.projects||{items:[]};
if(pending!==null&&(event>pending||s.error)){feedback(s.error||s.project_message);pending=null;if(!s.error)reset();}
for(const b of dialog.querySelectorAll('button,input,textarea,select'))if(b.id!=='projectClose')b.disabled=b.dataset.unavailable==='true'||pending!==null||s.recording||s.export?.status==='running';
const sig=JSON.stringify(catalog);if(sig===signature)return;signature=sig;
const active=catalog.items.find(p=>p.id===catalog.active);$('projectsBtn').textContent=(active?.name||'场景项目')+' ↗';
$('projectList').replaceChildren();const selected=$('projectSource').value;$('projectSource').replaceChildren(new Option('当前场景（包含未保存修改）','current'));
for(const p of catalog.items){$('projectSource').add(new Option(p.name,p.id));const card=document.createElement('article');card.className='project-card'+(p.id===catalog.active?' active':'');const title=document.createElement('b');title.textContent=p.name;const desc=document.createElement('p');desc.textContent=p.description||'暂无场景描述';const stamp=document.createElement('small');stamp.textContent=(p.id===catalog.active?'当前项目 · ':'')+'保存于 '+new Date(p.updated_at).toLocaleString();const actions=document.createElement('div');const open=document.createElement('button');open.textContent=p.id===catalog.active?'正在使用':'打开项目';open.disabled=p.id===catalog.active||!p.available;open.dataset.unavailable=String(open.disabled);open.onclick=()=>send({type:'project_switch',id:p.id});const edit=document.createElement('button');edit.textContent='编辑描述';edit.onclick=()=>{editing=p.id;$('projectFormTitle').textContent='编辑项目简报';$('projectName').value=p.name;$('projectDescription').value=p.description;$('projectSourceLabel').hidden=true;$('projectSubmit').textContent='保存描述';$('projectNew').hidden=false;};actions.append(open,edit);card.append(title,desc,stamp,actions);$('projectList').append(card);}
if([...$('projectSource').options].some(o=>o.value===selected))$('projectSource').value=selected;
}};
})();
