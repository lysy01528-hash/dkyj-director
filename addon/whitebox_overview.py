"""Shared-scene spatial overview; helpers never belong to the source scene."""
import json
import math
import re
import time
import bpy
from mathutils import Vector, Quaternion

MAX_ZONES = 8

def live_id(value, collection):
    try:
        return value is not None and collection.get(value.name) == value
    except ReferenceError:
        return False

def remove_unused_data(data):
    for collection in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras):
        if live_id(data, collection):
            if data.users == 0:
                collection.remove(data)
            return

def cleanup_saved_overviews():
    """Drop a disposable overview accidentally included by a manual Blender save."""
    for scene in list(bpy.data.scenes):
        if not live_id(scene, bpy.data.scenes) or not scene.get('previs_overview_owned'):
            continue
        data_blocks=[]
        for ob in list(scene.objects):
            if live_id(ob, bpy.data.objects) and ob.get('previs_overview_owned'):
                data_blocks.append(ob.data)
                bpy.data.objects.remove(ob,do_unlink=True)
        collections=list(scene.collection.children)
        world=scene.world
        bpy.data.scenes.remove(scene)
        for data in data_blocks:
            remove_unused_data(data)
        for collection in collections:
            if live_id(collection,bpy.data.collections) and collection.users==0 and not collection.objects:
                bpy.data.collections.remove(collection)
        if live_id(world,bpy.data.worlds) and world.users==0:bpy.data.worlds.remove(world)
    for mat in list(bpy.data.materials):
        if mat.get('previs_overview_owned') and mat.users==0:bpy.data.materials.remove(mat)

def _bounds(scene, floor_only=False):
    floor = next((o for o in scene.objects if o.name.split('.')[0]=='Floor'),None) if floor_only else None
    objects = [floor] if floor else [o for o in scene.objects if o.type == 'MESH' and not o.hide_render and not o.get('previs_bounds_ignore')]
    return [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box] or [Vector((-5,-4,0)), Vector((5,4,0))]

def validate_zones(zones):
    if not isinstance(zones, list) or len(zones) > MAX_ZONES:
        raise ValueError('最多支持 8 个空间分区')
    result, ids = [], set()
    for i, raw in enumerate(zones):
        if not isinstance(raw, dict):
            raise ValueError('空间分区格式不正确')
        z = {k: str(raw.get(k, default)).strip()[:limit] for k, default, limit in
             [('id', 'zone-'+str(i+1), 64), ('name', '区域 '+str(i+1), 32), ('description', '', 80)]}
        if not z['id'] or z['id'] in ids:
            raise ValueError('每个空间分区需要不同的编号')
        ids.add(z['id'])
        if not z['name']:
            raise ValueError('请填写分区名称')
        color = str(raw.get('color', '#808080'))
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            raise ValueError('请选择有效的分区颜色')
        z['color'] = color.upper()
        for key in ('x','y','z','width','depth','height'):
            try:
                number = float(raw.get(key, 3 if key == 'height' else 2 if key in ('width','depth') else 0))
            except (TypeError, ValueError):
                raise ValueError('分区坐标与宽深必须是数字')
            if not math.isfinite(number) or abs(number) > 10000:
                raise ValueError('分区坐标或宽深超出范围')
            if key in ('width','depth','height') and number < .01:
                raise ValueError('分区宽度和深度至少为 0.01')
            z[key] = number
        z['open_sky'] = bool(raw.get('open_sky', False))
        result.append(z)
    return result

def read_zones(scene):
    raw = scene.get('previs_zones')
    if raw is not None:
        return validate_zones(json.loads(raw) if isinstance(raw, str) else raw)
    points = _bounds(scene, floor_only=True)
    xmin,xmax = min(p.x for p in points),max(p.x for p in points)
    ymin,ymax = min(p.y for p in points),max(p.y for p in points)
    z = max(p.z for p in points) if next((o for o in scene.objects if o.name.split('.')[0]=='Floor'),None) else min(p.z for p in points)
    w,d = xmax-xmin,ymax-ymin
    height=max(p.z for p in _bounds(scene))-z
    return validate_zones([dict(id='room',name='室内空间',description='同一个房间共用一种颜色；只有连接到另一个空间时才新增分区。',
        color='#94B5AE',x=(xmin+xmax)/2,y=(ymin+ymax)/2,z=z,width=max(.1,w),depth=max(.1,d),height=max(2.4,height))])

def write_zones(scene, zones):
    zones = validate_zones(zones)
    scene['previs_zones'] = json.dumps(zones, ensure_ascii=False)
    return zones

def _curves(camera):
    ad = camera.animation_data
    if not ad or not ad.action:
        return []
    result=[]
    for layer in ad.action.layers:
        for strip in layer.strips:
            if strip.type == 'KEYFRAME':
                bag = strip.channelbag(ad.action_slot)
                if bag: result.extend(bag.fcurves)
    return result

def _route(camera):
    if camera is None or not ('previs_take_start' in camera or camera.get('previs_demo')):
        return [], []
    curves = {c.array_index:c for c in _curves(camera) if c.data_path == 'location'}
    if not all(i in curves for i in range(3)):
        return [], []
    start=int(camera.get('previs_take_start',camera.get('previs_demo_start',1)))
    end=int(camera.get('previs_take_end',camera.get('previs_demo_end',start)))
    frames = list(range(start,end+1,max(1,math.ceil((end-start)/160))))
    if frames[-1] != end: frames.append(end)
    return [Vector(tuple(curves[i].evaluate(f) for i in range(3))) for f in frames], frames

class OverviewRig:
    def __init__(self, source_scene):
        self.closed = False
        self.owned_data = []
        self.source_scene = source_scene
        self.scene = bpy.data.scenes.new('WB_Overview_'+source_scene.name)
        self.scene['previs_overview_owned'] = True
        self.collection = bpy.data.collections.new('WB_OverviewHelpers')
        self.collection['previs_overview_owned'] = True
        self.scene.collection.children.link(self.collection)
        self.objects, self.materials = [], []
        self.zones = read_zones(source_scene)
        zone_ids={z['id'] for z in self.zones}
        for ob in source_scene.objects:
            if not ob.hide_render and not ob.get('previs_overview_hide') and ob.get('previs_zone_id') not in zone_ids:
                self.scene.collection.objects.link(ob)
        self.zones = read_zones(source_scene)
        self.route, self.route_frames, self.route_object = [], [], None
        self.route_key, self.route_checked = None, 0
        self.label_mat = self.material('Labels','#18232C')
        self.yellow = self.material('Camera','#D5A33A')
        self.grid_mat = self.material('Grid','#D9DED8')
        self.dim_mat = self.material('Dimensions','#657B7D')
        self.frustum_objects=[]
        self.frustum_lens=None
        self.number_plates=[]
        self.base_location=None
        self.follow_anchor=None
        self.cutaway_objects=[]
        # Cutaway walls are independent copies: solid in POV, wire in the observer.
        for original in source_scene.objects:
            if original.get('previs_overview_hide') and original.type=='MESH' and not original.hide_render and not original.get('previs_bounds_ignore'):
                corners=[original.matrix_world @ Vector(c) for c in original.bound_box]
                for a,b in ((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)):
                    self.cutaway_objects.append(self.line('WBCutaway',[corners[a],corners[b]],self.dim_mat,.012))
        for i,z in enumerate(self.zones,1):
            mat=self.material('Zone_'+z['id'],z['color'])
            for floor in source_scene.objects:
                if floor.get('previs_zone_id')==z['id']:
                    data=floor.data.copy();data.materials.clear();data.materials.append(mat)
                    copy=self.object('WBZoneFloor_'+z['id'],data);copy.matrix_world=floor.matrix_world.copy()
            if not any(o.get('previs_zone_id')==z['id'] for o in source_scene.objects):self.box('WBZone_'+z['id'],(z['width'],z['depth'],.02),(z['x'],z['y'],z['z']+.025),mat)
            plate=self.box('WBZonePlate',(.64,.45,.045),(z['x']+z['width']*.32,z['y']+z['depth']*.15,z['z']+1.8),self.material('ZonePlate','#FAFBF6'))
            self.number_plates.append(plate)
            data=bpy.data.curves.new('WBZoneNumber','FONT');data.body=f'{i:02d}';data.size=.25;data.align_x='CENTER';data.extrude=.001
            ob=self.object('WBZoneLabel_'+z['id'],data);ob.parent=plate;ob.location=(0,-.09,.03);data.materials.append(self.label_mat)
            self.dimensions(z)
        self.camera=self.object('WBOverviewCamera',bpy.data.cameras.new('WBOverviewCameraData'));self.camera.data.type='ORTHO';self.scene.camera=self.camera
        self.camera_model=self.box('WBCameraBody',(.38,.25,.25),(0,0,0),self.yellow);self.camera_model.rotation_mode='QUATERNION'
        lens=self.box('WBCameraLens',(.18,.18,.18),(0,0,-.20),self.label_mat);lens.parent=self.camera_model
        self.camera_model.scale=(1,1,1)
        self.configure()
        self.grid()
        self.update(source_scene.camera)
        self.fit(source_scene.camera)

    def text(self,name,body,position,size=.23,angle=0):
        data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.materials.append(self.dim_mat)
        ob=self.object(name,data);ob.location=position;ob.rotation_euler[2]=angle;return ob

    def dimensions(self,z):
        unit=self.source_scene.unit_settings.scale_length
        x,y,h=z['x'],z['y'],z['z']+.07;w,d=z['width']/2,z['depth']/2
        for name,pts in [('Width',[(x-w,y-d-.5,h),(x+w,y-d-.5,h)]),('Depth',[(x+w+.5,y-d,h),(x+w+.5,y+d,h)])]:
            self.line('WBDimension'+name,pts,self.dim_mat,.01)
        for xx in (x-w,x+w):self.line('WBDimensionTick',[(xx,y-d-.65,h),(xx,y-d-.35,h)],self.dim_mat,.01)
        for yy in (y-d,y+d):self.line('WBDimensionTick',[(x+w+.35,yy,h),(x+w+.65,yy,h)],self.dim_mat,.01)
        self.text('WBWidth',f"{z['width']*unit:g} m",(x,y-d-.95,h))
        self.text('WBDepth',f"{z['depth']*unit:g} m",(x+w+.8,y,h),angle=math.pi/2)

    def grid(self):
        if not self.zones:return
        xmin=min(z['x']-z['width']/2 for z in self.zones)-3;xmax=max(z['x']+z['width']/2 for z in self.zones)+3
        ymin=min(z['y']-z['depth']/2 for z in self.zones)-3;ymax=max(z['y']+z['depth']/2 for z in self.zones)+3
        z=min(z['z'] for z in self.zones)-.2
        # At most 80 lines, including large imported scenes.
        step=max(1,math.ceil(max(xmax-xmin,ymax-ymin)/40))
        for x in range(math.floor(xmin),math.ceil(xmax)+1,step):self.line('WBGrid',[(x,ymin,z),(x,ymax,z)],self.grid_mat,.007)
        for y in range(math.floor(ymin),math.ceil(ymax)+1,step):self.line('WBGrid',[(xmin,y,z),(xmax,y,z)],self.grid_mat,.007)

    def frustum(self,cam):
        # view_frame includes sensor fit, aspect ratio and lens shift.
        frame=cam.data.view_frame(scene=self.source_scene)
        key=tuple(round(v,5) for p in frame for v in p)
        if key==self.frustum_lens:return
        for ob in self.frustum_objects:self.remove_object(ob)
        self.frustum_objects=[]
        corners=[tuple(p*(1.7/abs(p.z))) for p in frame]
        paths=[[(0,0,0),p] for p in corners]+[corners+[corners[0]],[(0,0,-.25),(0,0,-2.25)],[( -.12,0,-2.05),(0,0,-2.25),(.12,0,-2.05)]]
        for points in paths:
            ob=self.line('WBCameraFrustum',points,self.yellow,.013);ob.parent=self.camera_model;self.frustum_objects.append(ob)
        # Top marker makes roll and the camera's up direction legible.
        ob=self.line('WBCameraTop',[(-.13,.2,0),(0,.38,0),(.13,.2,0)],self.yellow,.022);ob.parent=self.camera_model;self.frustum_objects.append(ob)
        self.frustum_lens=key

    def object(self,name,data):
        ob=bpy.data.objects.new(name,data);self.collection.objects.link(ob);self.objects.append(ob);self.owned_data.append(data);ob['previs_overview_owned']=True;return ob

    def material(self,name,hx):
        # Blender stores linear RGB; convert from the same sRGB hex shown in the legend.
        def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
        mat=bpy.data.materials.new('WBOverview_'+name);mat['previs_overview_owned']=True;mat.diffuse_color=(*[linear(int(hx[i:i+2],16)/255) for i in (1,3,5)],1);self.materials.append(mat);return mat

    def box(self,name,size,location,material):
        x,y,z=(v/2 for v in size)
        verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update();mesh.materials.append(material)
        ob=self.object(name,mesh);ob.location=location;return ob

    def line(self,name,points,material,radius=.027):
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=0
        spline=data.splines.new('POLY');spline.points.add(len(points)-1)
        for pt,co in zip(spline.points,points):pt.co=(*co,1)
        data.materials.append(material);return self.object(name,data)

    def remove_object(self,ob):
        # External deletion may already have removed the object or its data.
        self.objects = [item for item in self.objects if item is not ob]
        if live_id(ob, bpy.data.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            self.owned_data = [item for item in self.owned_data if item is not data]
            remove_unused_data(data)

    def configure(self):
        s=self.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
        s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=False;s.display.shading.show_cavity=True
        s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('WBOverviewWorld');s.world.color=(.83,.85,.81)
        self.world = s.world
        s.view_settings.view_transform='Standard';s.render.fps=self.source_scene.render.fps;s.render.fps_base=self.source_scene.render.fps_base

    def fit(self,cam):
        points=_bounds(self.source_scene)
        if self.source_scene.get('previs_overview_top'):points.append(Vector((0,0,float(self.source_scene['previs_overview_top']))))
        points.extend(Vector(p) for p in json.loads(self.source_scene.get('previs_overview_extent','[]')))
        for z in self.zones:
            points.extend(Vector((z['x']+dx*(z['width']/2+1.2),z['y']+dy*(z['depth']/2+1.2),z['z'])) for dx in (-1,1) for dy in (-1,1))
        points += self.route
        ground=min((z['z'] for z in self.zones),default=0)+.085
        points.extend(Vector((p.x,p.y,ground)) for p in self.route)
        if cam: points.append(cam.matrix_world.translation.copy())
        center=sum(points,Vector())/len(points)
        # Look down from the open front of a room. Fit all projected bounds in 16:9.
        q=Vector((-.8,.8,-1.25)).to_track_quat('-Z','Y')
        inverse=q.inverted(); project=[inverse @ p for p in points]
        xmin,xmax=min(p.x for p in project),max(p.x for p in project)
        ymin,ymax=min(p.y for p in project),max(p.y for p in project)
        local_center=Vector(((xmin+xmax)/2,(ymin+ymax)/2,max(p.z for p in project)+20))
        self.camera.rotation_mode='QUATERNION';self.camera.rotation_quaternion=q;self.camera.location=q @ local_center
        self.camera.data.ortho_scale=max(xmax-xmin,(ymax-ymin)*16/9,4)*1.22
        self.camera.data.clip_end=max(1000,self.camera.data.ortho_scale*5)
        self.base_location=self.camera.location.copy();self.base_rotation=q.copy()
        self.follow_anchor=self.route[0].copy() if self.route else (cam.matrix_world.translation.copy() if cam else Vector())

    def update(self,camera=None,frame=None):
        if not self.is_valid():
            raise ReferenceError('空间总览的场景或辅助对象已移除，需要重建')
        cam=camera or self.source_scene.camera
        pose=cam.matrix_world.copy() if cam else None
        if frame is not None and self.scene.frame_current!=int(frame):self.scene.frame_set(int(frame))
        if cam:
            self.camera_model.matrix_world=pose
            self.frustum(cam)
            key=(cam.name,cam.get('previs_take_start'),cam.get('previs_take_end'))
            now=time.monotonic()
            if key!=self.route_key or now-self.route_checked>1:
                camera_changed=self.route_key is not None and key[0]!=self.route_key[0]
                self.route,self.route_frames=_route(cam);self.route_path=[tuple(p) for p in self.route]
                if self.route_object:self.remove_object(self.route_object);self.route_object=None
                if len(self.route)>1:
                    # Ground projection exposes the travelled path; body retains true elevation.
                    ground=min((z['z'] for z in self.zones),default=0)+.085
                    self.route_object=self.line('WBCameraRoute',[(p.x,p.y,ground) for p in self.route],self.yellow)
                self.route_key,self.route_checked=key,now
                if camera_changed:self.fit(cam)
            if self.base_location is not None:
                # Position-derived, bounded follow: identical for seek, live and export.
                delta=pose.translation-self.follow_anchor
                offset=Vector((math.tanh(delta.x/6)*.55,math.tanh(delta.y/6)*.55,math.tanh(delta.z/4)*.2))
                yaw=math.tanh(delta.y/6)*math.radians(1.8)
                self.camera.location=self.base_location+offset
                self.camera.rotation_quaternion=Quaternion((0,0,1),yaw) @ self.base_rotation
            for plate in self.number_plates:
                plate.rotation_mode='QUATERNION';plate.rotation_quaternion=self.camera.rotation_quaternion
        self.scene.view_layers[0].update()
        return self.scene

    def is_valid(self):
        if (self.closed or not live_id(self.source_scene, bpy.data.scenes)
                or not live_id(self.scene, bpy.data.scenes)
                or not live_id(self.collection, bpy.data.collections)
                or not live_id(self.camera, bpy.data.objects)
                or not live_id(self.camera.data, bpy.data.cameras)
                or not live_id(self.world, bpy.data.worlds)):
            return False
        if (self.scene.camera != self.camera or self.scene.world != self.world
                or self.scene.collection.children.get(self.collection.name) != self.collection):
            return False
        for obj in self.objects:
            if not live_id(obj, bpy.data.objects) or self.scene.objects.get(obj.name) != obj:
                return False
            if obj.data is None:
                return False
        return all(live_id(mat, bpy.data.materials) for mat in self.materials)

    def close(self):
        if self.closed:
            return
        self.closed = True
        for ob in list(self.objects):
            self.remove_object(ob)
        if live_id(self.scene, bpy.data.scenes):
            bpy.data.scenes.remove(self.scene)
        if live_id(self.collection, bpy.data.collections) and self.collection.users == 0:
            bpy.data.collections.remove(self.collection)
        for data in self.owned_data:
            remove_unused_data(data)
        for mat in self.materials:
            if live_id(mat, bpy.data.materials) and mat.users == 0:
                bpy.data.materials.remove(mat)
        if live_id(self.world, bpy.data.worlds) and self.world.users == 0:
            bpy.data.worlds.remove(self.world)
        self.objects = []; self.materials = []; self.owned_data = []
        self.scene = self.source_scene = self.collection = self.world = self.camera = None
        self.camera_model = self.route_object = None
        self.frustum_objects = []; self.number_plates = []
