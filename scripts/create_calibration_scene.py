import bpy, math, os, json
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); EX=os.path.join(ROOT,'examples'); QA=os.path.join(ROOT,'qa','demo')
BLEND=os.path.join(EX,'calibration_scene.blend'); PNG_SEATED=os.path.join(QA,'calibration_scene_seated.png'); PNG_STANDING=os.path.join(QA,'calibration_scene_standing.png'); VALIDATION=os.path.join(QA,'calibration_validation.json')
def material(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1); return m
WALL=material('Wall',(.62,.65,.69)); FLOOR=material('Floor',(.15,.17,.20)); WOOD=material('Wood',(.38,.2,.08)); RED=material('Red_Rig',(.9,.025,.015)); BLUE=material('Blue_Rig',(.025,.16,.9)); GLASS=material('Window_Glass',(.06,.48,.68)); BLACK=material('Facing_Marker',(.01,.01,.01))
def cube(n,l,sc,m,p=None):
 bpy.ops.mesh.primitive_cube_add(location=l); o=bpy.context.object; o.name=n; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); o.parent=p; return o
def sphere(n,l,r,m,p=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=l); o=bpy.context.object; o.name=n; o.data.materials.append(m); o.parent=p; return o
def pivot(n,p,l):
 o=bpy.data.objects.new(n,None); bpy.context.collection.objects.link(o); o.parent=p; o.location=l; o.rotation_mode='XYZ'; return o
def seg(n,p,length,r,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=length,location=(0,0,-length/2)); o=bpy.context.object; o.name=n; o.data.materials.append(m); o.parent=p; o.location=(0,0,-length/2); return o
def key(o,path,f): o.keyframe_insert(data_path=path,frame=f)
def pose(o,f,rot=None):
 if rot is not None: o.rotation_euler=tuple(math.radians(x) for x in rot); key(o,'rotation_euler',f)
def make_person(name,m,start,blue=False):
 root=bpy.data.objects.new(name+'_ROOT',None); bpy.context.collection.objects.link(root); root.location=start
 torso=cube(name+'_Torso',(0,0,1.38),(.27,.18,.42),m,root); head=sphere(name+'_Head',(0,0,2.02),.22,m,root); cube(name+'_Facing_Marker',(0,-.235,2.02),(.065,.07,.06),BLACK,head)
 limbs={}
 for side,label in [(-1,'L'),(1,'R')]:
  sh=pivot(f'{name}_{label}_Shoulder_PIVOT',root,(side*.30,0,1.62)); el=pivot(f'{name}_{label}_Elbow_PIVOT',sh,(0,0,-.46)); wr=pivot(f'{name}_{label}_Wrist_PIVOT',el,(0,0,-.40)); hip=pivot(f'{name}_{label}_Hip_PIVOT',root,(side*.15,0,1.00)); kn=pivot(f'{name}_{label}_Knee_PIVOT',hip,(0,0,-.54)); an=pivot(f'{name}_{label}_Ankle_PIVOT',kn,(0,0,-.52)); limbs[label]=(sh,el,wr,hip,kn,an)
  seg(f'{name}_{label}_UpperArm',sh,.46,.075,m); seg(f'{name}_{label}_Forearm',el,.40,.065,m); sphere(f'{name}_{label}_Hand',(0,0,-.43),.09,m,wr); seg(f'{name}_{label}_Thigh',hip,.54,.095,m); seg(f'{name}_{label}_Shin',kn,.52,.08,m); cube(f'{name}_{label}_Foot',(0,-.10,.055),(.11,.22,.055),m,an)
 if not blue:
  for f,pos in [(1,start),(72,(-1.45,1.55,0)),(120,(-.25,1.45,0)),(240,(-.25,1.45,0))]: root.location=pos; key(root,'location',f)
  for f,rz in [(1,0),(120,0),(144,-55),(168,-55),(192,0),(240,0)]: torso.rotation_euler[2]=math.radians(rz); head.rotation_euler[2]=math.radians(rz); key(torso,'rotation_euler',f); key(head,'rotation_euler',f)
  for label,(sh,el,wr,hip,kn,an) in limbs.items():
   sg=1 if label=='L' else -1
   for f,a,b in [(1,0,0),(48,20*sg,-18*sg),(96,-18*sg,18*sg),(120,0,0),(240,0,0)]: pose(sh,f,(0,a,0)); pose(el,f,(0,b,0))
 else:
  for f in (1,120):
   pose(torso,f,(-12,0,0))
   for sh,el,wr,hip,kn,an in limbs.values(): pose(hip,f,(35,0,0)); pose(kn,f,(-35,0,0)); pose(sh,f,(0,0,0)); pose(el,f,(0,0,0))
  for f in (168,192,240):
   pose(torso,f,(0,0,0))
   for sh,el,wr,hip,kn,an in limbs.values(): pose(hip,f,(0,0,0)); pose(kn,f,(0,0,0)); pose(sh,f,(0,0,0)); pose(el,f,(0,0,0))
 return root
def look(cam,t): cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler()
def main():
 os.makedirs(EX,exist_ok=True); os.makedirs(QA,exist_ok=True); bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False); s=bpy.context.scene; s.frame_start=1; s.frame_end=240; s.render.fps=24; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
 cube('Floor',(0,0,-.1),(4.5,3.2,.1),FLOOR); cube('Back_Wall_Left',(-2.7,3,2.2),(1.8,.1,2.2),WALL); cube('Back_Wall_Right',(2.7,3,2.2),(1.8,.1,2.2),WALL); cube('Back_Wall_Header',(0,3,3.7),(.9,.1,.7),WALL); cube('Window_Glass',(0,2.94,2.2),(.85,.03,1),GLASS); cube('Left_Wall',(-4.4,0,2.2),(.1,3,2.2),WALL); cube('Right_Wall',(4.4,0,2.2),(.1,3,2.2),WALL); cube('Table_Top',(-1.8,.4,1.25),(.9,.55,.1),WOOD)
 for x in (-2.5,-1.1): cube('Table_Leg',(x,.4,.6),(.08,.08,.6),WOOD)
 cube('Chair_Seat',(-1.8,-.7,.65),(.45,.45,.1),WOOD); cube('Chair_Back',(-1.8,-1.1,1.15),(.45,.08,.65),WOOD); make_person('Red',RED,(-2.6,1.8,0)); make_person('Blue',BLUE,(-1.8,-.7,0),True)
 bpy.ops.object.light_add(type='AREA',location=(0,-1,6)); bpy.context.object.data.energy=1800; bpy.context.object.data.size=5; bpy.ops.object.camera_add(location=(6.8,-7.5,5)); phone=bpy.context.object; phone.name='Camera_Phone'; phone.data.lens=35; look(phone,(0,1,1.25)); bpy.ops.object.camera_add(location=(6.8,-7.5,5)); demo=bpy.context.object; demo.name='Camera_Demo'; demo.data.lens=35
 for f,l in [(1,(9.5,-12,7)),(120,(8.5,-10,6.5)),(240,(7.5,-8,5.5))]: demo.location=l; look(demo,(0,1,1.25)); key(demo,'location',f); key(demo,'rotation_euler',f)
 s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=640; s.render.resolution_y=400; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.camera=demo; s.frame_set(96); s.render.filepath=PNG_SEATED; bpy.ops.render.render(write_still=True); s.frame_set(192); s.render.filepath=PNG_STANDING; bpy.ops.render.render(write_still=True); s.camera=phone; [ob.__setitem__('dkyj_saved_name',ob.name) for ob in bpy.context.scene.objects]; bpy.ops.wm.save_as_mainfile(filepath=BLEND)
 def world(n,f): s.frame_set(f); return list(bpy.data.objects[n].matrix_world.translation)
 seated=world('Blue_L_Foot',96); standing=world('Blue_L_Foot',192); marker_a=world('Red_Facing_Marker',120); marker_b=world('Red_Facing_Marker',168); cam=bpy.data.objects['Camera_Phone']; anim=bool(cam.animation_data and cam.animation_data.action)
 data={'fps':s.render.fps,'frame_end':s.frame_end,'metric':s.unit_settings.system,'phone_camera_has_animation':anim,'blue_left_foot_z_seated':seated[2],'blue_left_foot_z_standing':standing[2],'red_marker_positions_differ':marker_a!=marker_b,'joint_parent_chain':{'Red_L_Forearm':bpy.data.objects['Red_L_Forearm'].parent.name,'Red_L_UpperArm':bpy.data.objects['Red_L_UpperArm'].parent.name,'Blue_L_Shin':bpy.data.objects['Blue_L_Shin'].parent.name,'Blue_L_Thigh':bpy.data.objects['Blue_L_Thigh'].parent.name}}
 with open(VALIDATION,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
 print('CALIBRATION_SCENE',BLEND,PNG_SEATED,PNG_STANDING,VALIDATION)
if __name__=='__main__': main()
