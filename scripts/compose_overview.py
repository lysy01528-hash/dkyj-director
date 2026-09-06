"""Legend generation and isolated Blender 5.2 VSE composition helpers."""
import json, os, subprocess, sys, textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from platform_paths import project_python, chinese_font

def _legend_png(zones,path,meters_per_unit=1):
    from PIL import Image,ImageDraw,ImageFont
    fp=chinese_font()
    font=lambda size:ImageFont.truetype(fp,size)
    im=Image.new('RGB',(480,1080),(244,244,238));d=ImageDraw.Draw(im)
    d.text((32,24),'SPATIAL STUDY / CAMERA + BLOCKING',fill='#839181',font=font(13))
    d.text((32,54),'空间总览 · 同步机位',fill='#273838',font=font(25))
    d.line((32,104,448,104),fill='#D4DCD0')
    row=min(260,810/max(1,len(zones)));y=145
    title_size=22 if len(zones)<=4 else 16
    desc_size=17 if len(zones)<=4 else 12
    body=font(desc_size)
    for i,z in enumerate(zones):
        d.rounded_rectangle((32,y,64,y+32),radius=5,fill=z['color'])
        d.text((38,y+3),f'{i+1:02d}',fill='white',font=font(17))
        title=z['name'];sz=title_size
        while sz>11 and d.textlength(title,font=font(sz))>350:sz-=1
        d.text((82,y-1),title,fill='#273838',font=font(sz))
        dims=[z['width'],z['depth']]+([] if z.get('open_sky') else [z.get('height',3)])
        label=' × '.join(f'{v*meters_per_unit:g}' for v in dims)+' m'+(' / 露天' if z.get('open_sky') else '')
        d.text((82,y+26),label,fill='#65796C',font=font(13 if len(zones)>4 else 16))
        line='';lines=[]
        for c in z.get('description',''):
            if line and d.textlength(line+c,font=body)>350:lines.append(line);line=''
            line+=c
        if line:lines.append(line)
        # Dense legends keep every full description in the accompanying text/JSON.
        available=max(1,int((row-53)/(desc_size+4)))
        if len(lines)>available:lines=lines[:available];lines[-1]=lines[-1][:-1]+'…'
        for j,line in enumerate(lines):d.text((82,y+51+j*(desc_size+4)),line,fill='#889482',font=body)
        y+=row
    d.line((32,982,448,982),fill='#D4DCD0')
    d.text((32,1004),'金色＝摄影机与视锥 · 细线＝路径',fill='#7C8B79',font=font(15))
    d.text((32,1036),'近似尺寸 · 用于空间说明',fill='#7C8B79',font=font(15))
    im.save(path)

def create_legend(zones,path,meters_per_unit=1):
    """Pillow runs in the project venv, independently of Blender's Python ABI."""
    tmp=Path(path).with_suffix('.legend-data.json')
    tmp.write_text(json.dumps({'zones':zones,'meters_per_unit':meters_per_unit},ensure_ascii=False),encoding='utf-8')
    try:subprocess.run([str(project_python(ROOT)),str(Path(__file__)),'--legend-json',str(tmp),'--output',str(path)],check=True)
    finally:tmp.unlink(missing_ok=True)

def create_board(legend,overview,output):
    subprocess.run([str(project_python(ROOT)),str(Path(__file__)),'--board',str(legend),str(overview),str(output)],check=True)

def write_reference_text(zones,scene,camera,path,start,end,simplify=False):
    fps=scene.render.fps/scene.render.fps_base;unit=scene.unit_settings.scale_length
    subjects=json.loads(scene.get('previs_subjects','[]'));story=json.loads(scene.get('previs_story','[]'))
    lines=['白模参考说明 · '+str(scene.get('previs_title',scene.name)),
      f'本段 {(end-start+1)/fps:.2f} 秒，{fps:g} fps，镜头 {camera.name}。',
      '素材用法：纯镜头 MP4 提供最终机位、构图、镜头运动和角色动态；空间说明图／总览视频只说明布局、尺度、走位。',
      '不要把总览的俯视移动、摄影机小模型、轨迹线、尺寸线或拼版界面渲染进最终成片。',
      '上传参考图后，把下列角色与场景描述对应到实际素材编号；空间 JSON 是给人工或工具使用的辅助数据。','', '对应关系：']
    for a in subjects:lines.append(f"{a['id']} / {a['name']} / {a['color']}：{a.get('description','')}")
    for i,z in enumerate(zones,1):
        dims=[z['width'],z['depth']]+([] if z.get('open_sky') else [z.get('height',3)])
        label=' × '.join(f'{v*unit:g}' for v in dims)+' m'+('，开放上空' if z.get('open_sky') else '')
        lines.append(f"空间 {i:02d} / {z['name']} / {z['color']} / 约 {label}：{z['description']}")
    lines+=['','可粘贴提示词（先将 @视频1 指定为纯镜头 MP4）：',
      '参考 @视频1 的运镜、构图、景别变化、角色位置、动作轨迹和节奏，生成连续镜头。颜色块用于角色和空间对应，最终人物外观、环境、材质与光影按我提供的参考图或文字描述生成。']
    for a in subjects:lines.append(f"{a['color']} 模型对应 {a['name']}。{a.get('description','')}")
    if simplify:lines.append('人物简模只表达位移、朝向和头部姿态；请根据以下动作描述补全自然的四肢动作。')
    for b in story:
        if b['end']<start or b['start']>end:continue
        begin=(max(start,b['start'])-start)/fps;stop=(min(end,b['end'])-start+1)/fps
        lines.append(f"{begin:.2f}–{stop:.2f} 秒：{b['description']}")
    if not story:lines.append('按白模中的动作和镜头顺序连续推进，补全自然的四肢运动。')
    lines+=['保持空间连接关系、角色身份和物体尺度连贯。纯净画面，无尺寸文字、辅助线、相机模型和界面；声音与最终风格由我另行指定。','',
      '依据：Seedance 2.5 官方手册「（7）白模怎么写？」；核对日期 2026-09-06。',
      'https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e#LBsudhf9ZoRjNQx8UN0cX3pBn3P',
      '空间说明图、JSON、尺寸线和这份素材分工是本工具的工作流设计，不是平台强制上传格式。']
    Path(path).write_text('\n'.join(lines)+'\n',encoding='utf-8')

def write_zones_json(zones,scene,camera,path,start,end):
    samples=[]
    step=max(1,int(round(scene.render.fps/scene.render.fps_base/2)))
    for f in range(int(start),int(end)+1,step):
        scene.frame_set(f); p=camera.matrix_world.translation; q=camera.matrix_world.to_quaternion(); samples.append({'frame':f,'time_seconds':round((f-int(start))/(scene.render.fps/scene.render.fps_base),5),'lens_mm':round(camera.data.lens,3),'position':[round(v,5) for v in p],'rotation_quaternion':[round(v,6) for v in (q.x,q.y,q.z,q.w)]})
    if not samples or samples[-1]['frame'] != int(end):
        scene.frame_set(int(end)); p=camera.matrix_world.translation; q=camera.matrix_world.to_quaternion(); samples.append({'frame':int(end),'time_seconds':round((f-int(start))/(scene.render.fps/scene.render.fps_base),5),'lens_mm':round(camera.data.lens,3),'position':[round(v,5) for v in p],'rotation_quaternion':[round(v,6) for v in (q.x,q.y,q.z,q.w)]})
    Path(path).write_text(json.dumps({'zones':zones,'camera':camera.name,'fps':scene.render.fps/scene.render.fps_base,'fps_base':scene.render.fps_base,'coordinate_system':'Blender right-handed Z-up','quaternion_order':'xyzw','meters_per_unit':scene.unit_settings.scale_length,'scene_title':str(scene.get('previs_title',scene.name)),'subjects':json.loads(scene.get('previs_subjects','[]')),'story':json.loads(scene.get('previs_story','[]')),'lens_mm':camera.data.lens,'dimensions_note':'Approximate width, depth and height in scene units; multiply by meters_per_unit. Open-sky zones do not have a ceiling.','frame_start':int(start),'frame_end':int(end),'route_samples':samples},ensure_ascii=False,indent=2),encoding='utf-8')

def render_composition(source_scene,output,start,end,kind,**paths):
    import bpy
    comp=bpy.data.scenes.new('WB_Overview_Composite')
    comp.render.resolution_x=1920;comp.render.resolution_y=2160 if kind=='combined' else 1080
    comp.render.resolution_percentage=100;comp.render.pixel_aspect_x=comp.render.pixel_aspect_y=1
    comp.render.fps=source_scene.render.fps;comp.render.fps_base=source_scene.render.fps_base;comp.frame_start=start;comp.frame_end=end
    if hasattr(comp.render.image_settings,'media_type'):comp.render.image_settings.media_type='VIDEO'
    else:comp.render.image_settings.file_format='FFMPEG'
    comp.render.ffmpeg.format='MPEG4';comp.render.ffmpeg.codec='H264';comp.render.ffmpeg.audio_codec='NONE';comp.render.filepath=output
    strips=comp.sequence_editor_create().strips
    if kind=='combined':
        top=strips.new_movie('Spatial 16x9',paths['board_movie'],channel=1,frame_start=start)
        bottom=strips.new_movie('POV 16x9',paths['pov'],channel=2,frame_start=start)
        top.transform.offset_y=540;bottom.transform.offset_y=-540
        bottom.transform.scale_x=bottom.transform.scale_y=1.5
    else:
        top=strips.new_image('Spatial board 16x9',paths['board'],channel=1,frame_start=start)
        bottom=strips.new_movie('Observer viewport 16x9',paths['overview'],channel=2,frame_start=start)
        bottom.transform.scale_x=bottom.transform.scale_y=1.125;bottom.transform.offset_x=240
    for st in (top,bottom):st.frame_final_duration=end-start+1
    comp.view_settings.view_transform='Standard'
    old=bpy.context.window.scene if bpy.context.window else None
    try:
        if bpy.context.window:bpy.context.window.scene=comp
        bpy.ops.render.render(animation=True)
    finally:
        if bpy.context.window and old:bpy.context.window.scene=old
        bpy.data.scenes.remove(comp)

def compose(source_scene,pov,board_movie,output,start,end):
    render_composition(source_scene,output,start,end,'combined',pov=pov,board_movie=board_movie)

def compose_board(source_scene,overview,board,output,start,end):
    render_composition(source_scene,output,start,end,'board',overview=overview,board=board)

if __name__=='__main__':
    if '--legend-json' in sys.argv:
        a=sys.argv;data=json.loads(Path(a[a.index('--legend-json')+1]).read_text(encoding='utf-8'))
        _legend_png(data['zones'],a[a.index('--output')+1],data.get('meters_per_unit',1))
    elif '--board' in sys.argv:
        from PIL import Image,ImageDraw,ImageFont
        a=sys.argv;idx=a.index('--board');legend,overview,output=a[idx+1:idx+4]
        im=Image.new('RGB',(1920,1080),(244,244,238));im.paste(Image.open(legend).convert('RGB'),(0,0));im.paste(Image.open(overview).convert('RGB').resize((1440,810)),(480,135))
        d=ImageDraw.Draw(im);fp=chinese_font();font=ImageFont.truetype(fp,22)
        d.text((520,54),'DKYJ DIRECTOR / SPATIAL VIEW',font=font,fill='#64755C');d.text((1690,54),'16:9 / 1080p',font=font,fill='#64755C')
        d.text((520,996),'空间布局与镜头同步 · 原始观察画面保持 16:9',font=font,fill='#64755C');im.save(output)
