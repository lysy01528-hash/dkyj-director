(()=>{
 const $=s=>document.querySelector(s), token=new URLSearchParams(location.search).get('token')||'';
 const panel=$('#overviewPanel'),list=$('#zoneList'),status=$('#overviewStatus'),img=$('#overviewImage'),wait=$('#overviewImageWait');
 const editBtn=document.createElement('button');editBtn.id='editZones';editBtn.type='button';editBtn.className='overview-edit';$('#overviewClose').before(editBtn);
 let zones=[],revision=0,editing=false,dirty=false,pending=null,open=window.matchMedia('(min-width:951px)').matches,imageBusy=false,imageURL='',lastState={},notice='',noticeUntil=0;
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const clone=value=>JSON.parse(JSON.stringify(value));
 function say(message){notice=message;noticeUntil=Date.now()+8000;status.textContent=message}
 function normalize(z,i){return {id:String(z.id||`zone-${Date.now()}-${i}`),name:String(z.name??`分区 ${i+1}`).trim().slice(0,32),description:String(z.description||'').trim().slice(0,80),color:String(z.color||'#62BDA7').toUpperCase(),x:Number(z.x??0),y:Number(z.y??0),z:Number(z.z??0),width:Number(z.width??2),depth:Number(z.depth??2),height:Number(z.height??3),open_sky:!!z.open_sky}}
 const meters=()=>lastState.overview?.meters_per_unit||1;
 const size=z=>[z.width,z.depth,...(z.open_sky?[]:[z.height])].map(n=>(n*meters()).toFixed(1).replace(/\.0$/,'')).join(' × ')+' m'+(z.open_sky?' / 露天':'');
 function field(z,key,label,min){return `<label>${label}<input data-zone="${esc(z.id)}" data-key="${key}" type="number" step="0.01" ${min?`min="${min}"`:''} value="${esc(Math.round(z[key]*meters()*100)/100)}"></label>`}
 function rebuild(){
  list.innerHTML=zones.map((z,i)=>editing?`<article class="zone-card"><header><span class="zone-swatch" style="background:${esc(z.color)}"></span><b>${String(i+1).padStart(2,'0')}</b><button type="button" data-remove="${esc(z.id)}" aria-label="删除分区 ${i+1}">×</button></header><label>名称<input maxlength="32" data-zone="${esc(z.id)}" data-key="name" value="${esc(z.name)}"></label><label>一句话描述<input maxlength="80" data-zone="${esc(z.id)}" data-key="description" value="${esc(z.description)}"></label><label>分区颜色<input type="color" data-zone="${esc(z.id)}" data-key="color" value="${esc(z.color)}"></label><div class="zone-numbers">${field(z,'x','中心 X')}${field(z,'y','中心 Y')}${field(z,'z','地面 Z')}${field(z,'width','宽',.01)}${field(z,'depth','深',.01)}${field(z,'height','高',.01)}</div><label class="zone-open"><input data-zone="${esc(z.id)}" data-key="open_sky" type="checkbox" ${z.open_sky?'checked':''}>露天空间（不标室内高度）</label></article>`:`<article class="zone-readonly" data-zone-id="${esc(z.id)}"><span class="zone-number" style="background:${esc(z.color)}">${String(i+1).padStart(2,'0')}</span><b>${esc(z.name)}</b><span class="zone-size">≈ ${size(z)}</span><small>${esc(z.description||'待填写空间描述')}</small></article>`).join('')||'<p class="overview-empty">暂无分区 · 点击“编辑分区”添加。</p>';
  list.querySelectorAll('input').forEach(input=>input.addEventListener('input',()=>{const z=zones.find(z=>z.id===input.dataset.zone);if(z){z[input.dataset.key]=input.type==='number'?Number(input.value)/meters():input.type==='checkbox'?input.checked:input.value;dirty=true}}));
  list.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{zones=zones.filter(z=>z.id!==b.dataset.remove);dirty=true;rebuild()});
  panel.classList.toggle('is-editing',editing);document.body.classList.toggle('zones-editing',editing);editBtn.textContent=editing?'结束编辑':'编辑空间';$('.zone-actions').hidden=!editing;
 }
 function render(s){
  lastState=s;const o=s.overview;if(!o)return;
  $('#sceneTitle').textContent=s.scene_title||'空间与镜头，一起预演。';$('#sceneSubtitle').textContent=s.scene_subtitle||'同一时间轴上的空间总览与真实取景。';$('#sceneCount').textContent=(o.zones?.length||0)+' 个空间';$('#sceneLength').textContent=((s.frame_end-s.frame_start+1)/s.fps).toFixed(1)+' 秒排练';
  const subjects=s.subjects||[];$('#subjectLegend').innerHTML=subjects.map(a=>`<span><i style="background:${/^#[0-9a-f]{6}$/i.test(a.color)?a.color:'#888'}"></i><b>${esc(a.id)}</b>${esc(a.name)}</span>`).join('');
  const beats=s.story||[],current=beats.find(b=>s.frame>=b.start&&s.frame<=b.end);$('#beatLabel').textContent=current?current.label:'当前机位 / 自由取景';$('#storyBeats').innerHTML=beats.map(b=>`<span class="${b===current?'active':''}" style="flex:${Math.max(1,b.end-b.start+1)}" title="${esc(b.description)}">${esc(b.label)}</span>`).join('');
  const locked=!!s.recording||s.export?.status==='running';editBtn.disabled=locked||!!pending;
  $('#saveZones').disabled=locked||!!pending;$('#addZone').disabled=locked||!!pending||zones.length>=8;
  $('#exportOverviewBtn').disabled=locked||!(s.recorded_take?.frames>=2);$('#exportSpatialBtn').disabled=locked||!(s.recorded_take?.frames>=2);
  $('#exportBtn').textContent=s.export?.status==='running'?'导出中…':'镜头 16:9';
  if(pending){
   if(o.revision!==pending.revision){
    const matches=JSON.stringify((o.zones||[]).map(normalize))===JSON.stringify(pending.zones);
    if(matches){zones=clone(pending.zones);revision=o.revision;pending=null;dirty=false;editing=false;rebuild();say('分区已保存到 Blender 工程')}
    else{pending=null;say('分区已被其他窗口更新，当前编辑内容仍保留，请核对后保存')}
   }else if(s.error&&s.error!==pending.previousError){pending=null;say('保存失败：'+s.error)}
   else if(Date.now()-pending.started>8000){pending=null;say('尚未确认保存，请检查连接后重试；当前编辑内容已保留')}
  }
  if(!editing&&!dirty&&!pending&&Array.isArray(o.zones)&&JSON.stringify(zones)!==JSON.stringify(o.zones.map(normalize))){zones=o.zones.map(normalize);revision=o.revision;rebuild()}
  if(pending)status.textContent='正在等待 Blender 确认保存…';
  else if(Date.now()>noticeUntil)status.textContent=o.error?o.error:`${s.camera?.includes('Demo')?'示范机位':'当前机位'} · F ${String(o.frame??s.frame??1).padStart(4,'0')}${dirty?' · 有未保存修改':''}`;
  list.querySelectorAll('[data-zone-id]').forEach(el=>el.classList.toggle('active',el.dataset.zoneId===o.active_zone));
  const downloads=$('#overviewDownloads');downloads.innerHTML=(s.export?.files||[]).map(f=>`<a href="${esc(f.url)}" download>${esc(f.label)}</a>`).join('');
 }
 async function refreshImage(){
  if(!open||imageBusy)return;imageBusy=true;const ac=new AbortController(),timer=setTimeout(()=>ac.abort(),4000);
  try{
   const r=await fetch('/overview.png?token='+encodeURIComponent(token)+'&n='+Date.now(),{signal:ac.signal});if(!r.ok)throw Error('HTTP '+r.status);
   const next=URL.createObjectURL(await r.blob());img.onload=()=>{if(imageURL)URL.revokeObjectURL(imageURL);imageURL=next;wait.hidden=true};img.onerror=()=>{URL.revokeObjectURL(next);wait.hidden=false};img.src=next;
  }catch(e){wait.hidden=false;wait.textContent='等待空间总览…'}finally{clearTimeout(timer);imageBusy=false}
 }
 function setOpen(value){open=value;panel.hidden=!open;document.body.classList.toggle('overview-open',open);$('#overviewBtn').setAttribute('aria-expanded',String(open));$('#overviewBtn').textContent=open?'返回取景':'空间总览';$('#overviewClose').textContent=window.innerWidth>950?'镜头视图 ↗':'返回取景 ×';if(open){rebuild();refreshImage()}}
 function toggle(){setOpen(!open)}
 $('#overviewBtn').onclick=toggle;$('#overviewClose').onclick=()=>{if(open)toggle()};
 editBtn.onclick=()=>{if(lastState.recording||lastState.export?.status==='running')return;editing=!editing;if(editing)window.dispatchEvent(new CustomEvent('previs-overview-editing',{detail:true}));rebuild()};
 $('#addZone').onclick=()=>{if(lastState.recording||pending||zones.length>=8)return;zones.push(normalize({color:['#62BDA7','#719FE0','#DFAA5A','#D9879C','#9189D1','#92B36B','#59B5C4','#C79B7A'][zones.length]},zones.length));dirty=true;rebuild()};
 $('#saveZones').onclick=()=>{
  if(!editing||pending||lastState.recording||!window.previsControl)return;
  const data=zones.map(normalize);
  if(data.some(z=>!z.name.trim()||!Number.isFinite(z.x)||!Number.isFinite(z.y)||!Number.isFinite(z.z)||!Number.isFinite(z.width)||!Number.isFinite(z.depth)||!Number.isFinite(z.height)||z.width<.01||z.depth<.01||z.height<.01)){say('请填写名称和有效坐标，宽度、深度至少为 0.01');return}
  pending={zones:clone(data),revision:lastState.overview?.revision??revision,started:Date.now(),previousError:lastState.error};
  window.previsControl({type:'zones',zones:data});say('正在等待 Blender 确认保存…');
 };
 $('#exportOverviewBtn').onclick=()=>{const take=lastState.recorded_take;if(take?.frames>=2&&!lastState.recording){window.previsControl({type:'export',camera:take.name,mode:'overview',simplify:$('#simplifyExport').checked});say('正在导出空间总览和镜头')}};
 $('#exportSpatialBtn').onclick=()=>{const take=lastState.recorded_take;if(take?.frames>=2&&!lastState.recording){window.previsControl({type:'export',camera:take.name,mode:'spatial'});say('正在单独导出空间 16:9')}};
 window.previsOverview={render,canSwitchProject:()=>!editing&&!dirty&&!pending};rebuild();setOpen(open);setInterval(refreshImage,400);
 window.matchMedia('(min-width:951px)').addEventListener('change',e=>{if(!editing)setOpen(e.matches)});
 $('#downloadLink').addEventListener('click',e=>{if((lastState.export?.files||[]).length>1){e.preventDefault();$('#overviewDownloads').hidden=!$('#overviewDownloads').hidden}});
 window.previsExportOptions=()=>({simplify:$('#simplifyExport').checked});
})();
