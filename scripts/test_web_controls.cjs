/* Node-only behavioral harness for web/app.js. It never opens a browser or Blender. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'web', 'app.js'), 'utf8');

let now = 0; const intervals=[]; const listeners={}; const sent=[]; let activeFetch=0, maxFetch=0;
const els={};
function el(id, tag='DIV'){return els[id] ||= {id,tagName:tag,style:{},hidden:false,disabled:false,value:'',textContent:'',innerHTML:'',classList:{add(){},remove(){},toggle(){}},setAttribute(){},removeAttribute(){},setPointerCapture(){},addEventListener(){},append(){},querySelector(){return {style:{transform:''}}}}}
['cameraSelect','sensorBtn','calibrateBtn','resetBtn','frame','frameWait','statusDot','connectionText','fpsText','cameraName','takeName','frameText','timeText','recordBadge','sensorBanner','recordStatus','timeline','playBtn','stopBtn','recordBtn','exportBtn','downloadLink','speed','lens','speedValue','lensValue','startText','durationText','endText','toast','lookPad','joystick'].forEach(id=>el(id,id==='cameraSelect'?'SELECT':'DIV'));
els.timeline.value='1'; els.speed.value='1'; els.lens.value='35'; els.joystick.querySelector=()=>el('joyKnob'); el('joyKnob');
const document={activeElement:{tagName:'BODY'},querySelector(sel){return sel[0]==='#'?el(sel.slice(1)):null},querySelectorAll(sel){return sel==='[data-move]'?[]:[]},createElement(tag){return el('created-'+tag+Math.random(),tag.toUpperCase())},addEventListener(type,fn){(listeners['document:'+type] ||= []).push(fn)}};
const window={onkeydown:null,onkeyup:null,location:{search:'?token=test'},isSecureContext:true,orientation:0,addEventListener(type,fn){(listeners[type] ||= []).push(fn)},removeEventListener(){},setTimeout(fn,ms){return setTimeout(fn,ms)}};
const screen={orientation:{angle:0}};
function response(body={ok:true}){return Promise.resolve({ok:true,status:200,json:async()=>body,blob:async()=>new Blob(['x'])})}
function fetchMock(url, opts){const control=!!opts?.body;if(control){activeFetch++;maxFetch=Math.max(maxFetch,activeFetch);sent.push({url,body:JSON.parse(opts.body)})}return new Promise(resolve=>setImmediate(()=>{if(control)activeFetch--;resolve(response())}))}
const context={window,document,location:window.location,screen,URLSearchParams,fetch:fetchMock,Blob,URL:{createObjectURL:()=>`blob:${sent.length}`,revokeObjectURL:()=>{}},navigator:{onLine:true},setInterval(fn){intervals.push(fn);return intervals.length},setTimeout(fn,ms=0){if(ms<200)setImmediate(fn);return 0},clearTimeout(){},Date:{now:()=>now},Math,JSON,Error,console};
context.globalThis=context; context.window.document=document;
window.__step=()=>intervals.forEach(fn=>fn());
const injected=source.replace(/\n\}\)\(\);\s*$/, '\nwindow.__hooks={orientation,render,step:()=>window.__step(),state:()=>({sensorOn,base,gyroReady,gyroLatest,move:[...move],pendingLook:[...pendingLook],inputDirty,zeroPending,discrete:discrete.map(x=>x.body),commandBusy,continuousBusy}),enableSensor:()=>{sensorOn=true;base=null;gyroReady=false;gyroLatest=null;}};\n})();');
vm.runInNewContext(injected,context,{filename:'web/app.js'});
const h=context.window.__hooks;
const settle=()=>new Promise(resolve=>setImmediate(resolve));
async function tick(ms=50){now+=ms; h.step(); await settle(); await settle()}

(async()=>{
  h.render({connected:true,frame:1,frame_start:1,frame_end:240,fps:24,cameras:['Camera_Phone'],camera:'Camera_Phone',speed:1,lens:35});
  window.onkeydown({key:'w',preventDefault(){}});
  for(let i=0;i<9;i++) await tick(50);
  assert(sent.filter(x=>x.body?.type==='input'&&x.body.move[1]===1).length>=2,'held W did not heartbeat');
  window.onkeyup({key:'w'}); await tick(50); await tick(50);
  const lastInput=sent.filter(x=>x.body?.type==='input').at(-1).body; assert.deepEqual(lastInput.move,[0,0,0],'keyup did not send zero');

  h.enableSensor(); h.orientation({alpha:0,beta:0,gamma:0}); await tick(); h.orientation({alpha:0,beta:0,gamma:0});
  window.onkeydown({key:'d',preventDefault(){}}); await tick(); await tick(); window.onkeyup({key:'d'}); await tick();
  const kinds=sent.map(x=>x.body?.type).filter(Boolean); assert(kinds.includes('sensor_base')&&kinds.includes('orientation'),'gyro was not sent'); assert(kinds.includes('input'),'input was starved by gyro');
  const ori=sent.find(x=>x.body?.type==='orientation').body.quaternion; assert(Math.hypot(ori[0],ori[1],ori[2])<1e-6&&Math.abs(ori[3]-1)<1e-6,'relative identity was not preserved');

  els.recordBtn.onclick(); els.stopBtn.onclick(); await tick(); await tick(); const commands=sent.map(x=>x.body?.type).filter(x=>x==='record'||x==='stop'); assert.deepEqual(commands.slice(-2),['record','stop'],'record/stop FIFO failed'); assert.equal(maxFetch,1,'more than one control request was in flight');
  h.render({connected:true,recording:true,record_status:'recording',frame:20,frame_start:1,frame_end:240,fps:24,cameras:['Camera_Phone','Camera_Demo'],camera:'Camera_Phone'});
  h.enableSensor(); h.orientation({alpha:10,beta:4,gamma:2}); await tick(); const beforeQuiet=sent.length;
  h.render({connected:true,recording:false,record_status:'ready',control_hold:true,recorded_take:{name:'Camera_Take_01',frames:20,start:1,end:20,duration:0.8},frame:20,frame_start:1,frame_end:240,fps:24,cameras:['Camera_Phone','Camera_Demo'],camera:'Camera_Demo'});
  for(let i=0;i<6;i++)await tick(50); assert.equal(sent.length,beforeQuiet,'auto-stop did not keep controls quiet'); assert.equal(els.sensorBtn.textContent,'继续取景','control_hold did not expose resume action'); assert.equal(els.cameraSelect.value,'Camera_Demo','camera selection did not sync');
  els.sensorBtn.onclick(); await tick(); await tick(); assert(sent.some(x=>x.body?.type==='resume_live'),'resume action did not enqueue resume_live');
  console.log('web controls behavioral checks passed',JSON.stringify({inputHeartbeats:sent.filter(x=>x.body?.type==='input').length,commands:commands.slice(-2),maxFetch,autoStopHeld:true,resume:true}));
})().catch(e=>{console.error('web controls behavioral check failed:',e.message);process.exitCode=1});
