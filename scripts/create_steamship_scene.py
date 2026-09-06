"""Build the replaceable 10-second steamship blocking scene (meters, editable keys)."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'addon'))
from whitebox_overview import write_zones

def material(name,hx):
    c=[int(hx[i:i+2],16)/255 for i in (1,3,5)]
    c=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c]
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m

def mesh(name,verts,faces,mat,parent=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.materials.append(mat);data.update()
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);ob.parent=parent;return ob

def cube(name,loc,size,mat,parent=None):
    x,y,z=(v/2 for v in size)
    ob=mesh(name,[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,parent);ob.location=loc;return ob

def cylinder(name,loc,radius,depth,mat,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=depth,location=loc)
    ob=bpy.context.object;ob.name=name;ob.parent=parent;ob.data.materials.append(mat);return ob

def sphere(name,loc,radius,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=radius,location=loc)
    ob=bpy.context.object;ob.name=name;ob.parent=parent;ob.data.materials.append(mat);return ob

def empty(name,loc=(0,0,0),parent=None):
    ob=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(ob);ob.parent=parent;ob.location=loc;return ob

def key(ob,path,frame):ob.keyframe_insert(data_path=path,frame=frame)
def aim(ob,target):ob.rotation_quaternion=(Vector(target)-ob.location).to_track_quat('-Z','Y')
def curves(ob):
    if ob.animation_data and ob.animation_data.action:
        for layer in ob.animation_data.action.layers:
            for strip in layer.strips:
                if strip.type=='KEYFRAME':
                    bag=strip.channelbag(ob.animation_data.action_slot)
                    if bag:yield from bag.fcurves

def main():
    # Run in a factory-startup process; never delete the user's active scene.
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    s=bpy.context.scene;s.name='Steamship';s.frame_start=1;s.frame_end=240;s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s['previs_title']='蒸汽小船 · 舱内到甲板';s['previs_subtitle']='角色跑出船舱，飞机掠过头顶。'
    s['previs_story']=json.dumps([{'start':1,'end':84,'label':'跑出船舱','description':'角色 A 从船舱起跑，双臂前后交替摆动、左右腿交替抬膝蹬地，穿过打开的舱门。'}, {'start':85,'end':132,'label':'甲板减速','description':'角色 A 跑上前甲板，以两步缓冲减速，双脚站稳并抬头。'}, {'start':133,'end':216,'label':'飞机掠过','description':'角色 A 仰头追随飞机；固定翼螺旋桨飞机从左舷上空飞向右舷，机翼保持刚性，螺旋桨旋转。'}, {'start':217,'end':240,'label':'视线跟随','description':'飞机飞离船体上方，角色 A 保持站立并顺势转头目送。'}],ensure_ascii=False)
    s['previs_subjects']=json.dumps([{'id':'A','object':'Actor_A_ROOT','color':'#BD5147','name':'角色 A','description':'红色人物，跑出船舱的主角；角色外观由后续参考图指定。'}, {'id':'P','object':'Airplane_ROOT','color':'#688CA1','name':'飞机','description':'蓝灰色固定翼螺旋桨飞机，机头朝飞行方向；外观由后续参考图指定。'}],ensure_ascii=False)
    deck=material('02 Deck','#C6AD78');cabin=material('01 Cabin','#8FAEA7');ivory=material('Paint','#DDDCD0');dark=material('Steel','#4F6269');wood=material('Furniture','#A6AAA0');water=material('Water','#B5C9CA');red=material('Actor A','#BD5147');plane=material('Airplane','#688CA1');black=material('Facing','#333F43')
    # Hull: pointed bow, shallow aft taper, broad usable deck.
    outline=[(-2.5,-6.2),(2.5,-6.2),(2.8,4.8),(1.55,6.7),(0,7.5),(-1.55,6.7),(-2.8,4.8)]
    verts=[(x,y,.26) for x,y in outline]+[(x*.72,y*.91,-1.3) for x,y in outline];n=len(outline)
    hull=mesh('Hull',verts,[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],dark)
    floor=mesh('Floor',[(x,y,.31) for x,y in outline],[tuple(range(n))],deck)
    sea=cube('Sea',(0,0,-1.15),(300,300,.05),water);sea['previs_bounds_ignore']=True;sea['previs_overview_hide']=True
    # Cabin: door opens directly onto the forward deck. Roof/walls stay solid in POV.
    cabin_floor=cube('Cabin_Floor',(0,-2.4,.34),(4.2,4.8,.06),cabin);cabin_floor['previs_zone_id']='cabin';floor['previs_zone_id']='deck'
    for name,loc,size in [('Cabin_Left',(-2.1,-2.4,1.72),(.12,4.8,2.76)),('Cabin_Right',(2.1,-2.4,1.72),(.12,4.8,2.76)),('Cabin_Aft',(0,-4.8,1.72),(4.2,.12,2.76)),('Cabin_Roof',(0,-2.4,3.13),(4.45,5.0,.14))]:
        ob=cube(name,loc,size,ivory);ob['previs_overview_hide']=True
    for x in (-1.4,1.4):cube('Cabin_Door_Wall',(x,0,1.72),(1.4,.14,2.76),ivory)
    cube('Cabin_Door_Lintel',(0,0,2.9),(1.4,.14,.40),ivory)
    door=empty('Door_Hinge',(-.7,-.08,.35));door.rotation_euler.z=math.radians(100)
    cube('Cabin_Open_Door',(.65,0,1.15),(1.3,.10,2.3),cabin,door)
    # Spare furniture kept away from the walk-through lane.
    cube('Bunk',(-1.47,-2.85,.79),(.9,2.35,.8),wood);cube('Bunk_Mattress',(-1.47,-2.85,1.23),(.94,2.38,.13),ivory)
    cube('Desk',(1.40,-3.75,1.08),(.9,1.3,.14),wood)
    for y in (-4.2,-3.3):cube('Desk_Leg',(1.4,y,.7),(.1,.1,.7),dark)
    cube('Cabinet',(1.5,-1.35,1.05),(.8,1.2,1.4),wood)
    for y in (-3.9,-1.6):
        win=cylinder('Porthole',(2.02,y,1.95),.29,.08,dark);win.rotation_euler.y=math.pi/2
    # Steam funnel at aft; forward sight line remains open.
    cylinder('Funnel_Base',(0,-3.1,3.4),.61,.55,dark)
    cylinder('Steam_Funnel',(0,-3.1,4.2),.43,1.3,wood)
    cylinder('Funnel_Rim',(0,-3.1,4.85),.50,.18,dark)
    for i in range(3):
        ob=sphere('Steam_Puff',(.1*i,-3.1-.27*i,5.1+.35*i),.22+.08*i,ivory);ob['previs_bounds_ignore']=True
        for f in (1,60,120,180,240):
            ob.location.x=.15*i+.15*math.sin(f/35+i);ob.location.z=5.1+.35*i+.10*math.sin(f/40+i);key(ob,'location',f)
    for x in (-2.55,2.55):
        for y in (-5.7,-4.2,-2.7,-1.2,.5,2,3.5,4.8):cylinder('Rail_Post',(x,y,.91),.045,1.15,dark)
        for z in (.85,1.43):cube('Rail',(x,-.5,z),(.06,10.6,.06),ivory)
    cube('Aft_Rail',(0,-5.9,1.43),(5.1,.06,.06),ivory)
    for x in (-1.8,1.8):
        for y in (1,2.1):cube('Cargo_Crate',(x,y,.72),(.85,.82,.8),wood)
        cylinder('Bollard',(x,4.75,.58),.12,.52,dark)
    cube('Bow_Bench',(0,5.25,.8),(2,.48,.16),wood)
    for x in (-.8,.8):cube('Bench_Leg',(x,5.25,.55),(.12,.3,.45),dark)
    # Actor: stable identity color, editable body/limb rotations. Forward is +Y.
    root=empty('Actor_A_ROOT');root['previs_subject']='A'
    body=cube('Actor_A_Body',(0,0,1.10),(.45,.30,.65),red,root)
    head=empty('Actor_A_Head_Pivot',(0,0,1.52),root)
    sphere('Actor_A_Head',(0,0,.10),.20,red,head)
    cube('Actor_A_Facing',(0,.192,.10),(.11,.045,.07),black,head)
    limbs=[]
    for side in (-1,1):
        hip=empty('Actor_A_Hip',(side*.13,0,.80),root)
        upper=cylinder('Actor_A_Thigh',(0,0,-.20),.082,.40,red,hip)
        knee=empty('Actor_A_Knee',(0,0,-.39),hip)
        lower=cylinder('Actor_A_Shin',(0,0,-.17),.065,.34,red,knee)
        foot=cube('Actor_A_Foot',(0,.085,-.35),(.14,.28,.10),red,knee)
        shoulder=empty('Actor_A_Shoulder',(side*.29,0,1.35),root)
        arm=cylinder('Actor_A_UpperArm',(0,0,-.15),.057,.3,red,shoulder)
        elbow=empty('Actor_A_Elbow',(0,0,-.30),shoulder)
        forearm=cylinder('Actor_A_Forearm',(0,0,-.15),.052,.30,red,elbow)
        for ob in (upper,lower,foot,arm,forearm):ob['previs_ai_hide']=True
        limbs.append((side,hip,knee,shoulder,elbow))
    # Simple AI export torso extends to the same ground contact; preview keeps limbs.
    proxy=cube('Actor_A_AI_Proxy',(0,0,.53),(.42,.3,.94),red,root);proxy.hide_render=True;proxy.hide_viewport=True;proxy['previs_ai_show']=True
    positions=[(1,-2.3),(12,-2.2),(36,-1.35),(60,-.55),(84,1.05),(108,2.75),(125,3.75),(144,3.85),(240,3.85)]
    for f,y in positions:root.location=(0,y,.35);key(root,'location',f)
    for f in range(1,241,3):
        activity=min(1,max(0,(f-1)/12))*max(0,min(1,(132-f)/22))
        phase=(f-1)*math.pi/6
        root.rotation_euler.x=math.radians(-8*activity);key(root,'rotation_euler',f)
        for side,hip,knee,shoulder,elbow in limbs:
            wave=math.sin(phase+(0 if side==1 else math.pi))
            hip.rotation_euler.x=math.radians(wave*30*activity)
            knee.rotation_euler.x=math.radians(-max(0,-wave)*60*activity)
            shoulder.rotation_euler.x=math.radians(-wave*38*activity)
            elbow.rotation_euler.x=math.radians(-65*activity)
            for ob in (hip,knee,shoulder,elbow):key(ob,'rotation_euler',f)
    for f,rx,rz in [(1,0,0),(126,0,0),(145,32,-25),(170,44,0),(208,38,48),(240,25,65)]:
        head.rotation_euler=(math.radians(rx),0,math.radians(rz));key(head,'rotation_euler',f)
    # Fixed-wing propeller plane, travelling from port to starboard (+X).
    air=empty('Airplane_ROOT');air.scale=(.83,.83,.83);air['previs_subject']='P'
    fuselage=sphere('Aircraft_Fuselage',(0,0,0),1,plane,air);fuselage.scale=(2.5,.34,.38)
    cube('Aircraft_Wings',(.05,0,0),(1.1,6.8,.12),plane,air)
    cube('Aircraft_Tailplane',(-1.8,0,.1),(.7,2.2,.10),plane,air)
    cube('Aircraft_Fin',(-1.8,0,.52),(.78,.1,.9),plane,air)
    cockpit=sphere('Aircraft_Cockpit',(.4,0,.30),.35,black,air);cockpit.scale=(1.5,.75,.65)
    prop=empty('Aircraft_Propeller',(2.4,0,0),air);cube('Aircraft_Prop_Blade',(0,0,0),(.08,.14,1.8),dark,prop)
    for f in (1,240):prop.rotation_euler.x=f*math.pi/3;key(prop,'rotation_euler',f)
    for f,x in [(1,-62.6),(120,-18),(168,0),(216,18),(240,27)]:air.location=(x,3.85,7.2);key(air,'location',f)
    for ob in [air]+list(air.children_recursive):ob['previs_bounds_ignore']=True
    # Keep overview framing stable while the plane enters and leaves the view.
    bound=empty('Overview_Flight_Height',(0,0,0));bound['height']=7.6
    s['previs_overview_top']=8.0;s['previs_overview_extent']=json.dumps([[-3,1,6.5],[3,6.8,8.0]])
    # Authored demo and an independent camera ready for the user's phone take.
    demo=bpy.data.objects.new('Camera_Demo',bpy.data.cameras.new('Camera_Demo'));s.collection.objects.link(demo);demo.rotation_mode='QUATERNION';demo.data.lens=20
    demo['previs_demo']=True;demo['previs_demo_start']=1;demo['previs_demo_end']=240
    camera_keys=[(1,(-.3,-4.4,1.85),(0,-2.1,1.25)),(48,(-.3,-3.4,1.9),(0,-.6,1.4)),(96,(-.25,-.25,1.95),(0,3.1,1.4)),(126,(-1.35,2.0,1.8),(0,3.85,1.45)),(144,(-1.45,2,1.85),(-4.4,3.85,6.7)),(168,(-1.3,1.9,1.95),(0,3.85,7.2)),(192,(-1.15,1.8,1.95),(7,3.85,7.2)),(216,(-1,1.8,1.95),(13,3.85,7.2)),(240,(-1,1.8,1.95),(16,3.85,7.2))]
    previous=None
    for f,pos,target in camera_keys:
        demo.location=pos;aim(demo,target)
        if previous and previous.dot(demo.rotation_quaternion)<0:demo.rotation_quaternion.negate()
        previous=demo.rotation_quaternion.copy();key(demo,'location',f);key(demo,'rotation_quaternion',f)
    for ob in bpy.data.objects:
        for c in curves(ob):
            for k in c.keyframe_points:
                k.interpolation='LINEAR' if ob==air or ob==prop or ob==root or ob.name.startswith('Actor_A_Hip') or ob.name.startswith('Actor_A_Knee') else 'BEZIER'
                k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
    s.frame_set(1);bpy.context.view_layer.update()
    phone=bpy.data.objects.new('Camera_Phone',demo.data.copy());s.collection.objects.link(phone);phone.matrix_world=demo.matrix_world.copy();phone.rotation_mode='QUATERNION'
    s.camera=demo
    for f,label in [(1,'起跑'),(84,'出舱'),(132,'抬头'),(168,'飞机掠顶'),(216,'飞离')]:s.timeline_markers.new(label,frame=f)
    write_zones(s,[dict(id='cabin',name='船舱',description='舱内靠墙设置卧铺与柜台，中央留出通向前甲板的舱门和跑动通道。',color='#8FAEA7',x=0,y=-2.4,z=.37,width=4.2,depth=4.8,height=2.76),dict(id='deck',name='前甲板',description='露天甲板两侧有栏杆与木箱，人物出舱后在中部停下，飞机从上空横向掠过。',color='#C6AD78',x=0,y=3.5,z=.32,width=5.6,depth=7,height=7,open_sky=True)])
    s['previs_zones_revision']=1;s['previs_zone_floors']=True
    s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
    s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD'
    s.world.color=(.65,.73,.76);s.view_settings.view_transform='Standard';s.camera=demo
    s.frame_set(1)
    path=ROOT/'examples/steamship_scene.blend';[ob.__setitem__('dkyj_saved_name',ob.name) for ob in bpy.context.scene.objects]; bpy.ops.wm.save_as_mainfile(filepath=str(path))
    print('STEAMSHIP_READY',path,'objects',len(s.objects))

if __name__=='__main__':main()
