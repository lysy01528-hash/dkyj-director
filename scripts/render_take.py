"""Render a clean POV take, optionally with a synchronized spatial overview."""
import sys
import bpy
from pathlib import Path
arguments = sys.argv[sys.argv.index('--') + 1:]
output, start, end = arguments[:3]
recorded_name = arguments[3] if len(arguments) > 3 else None
mode = arguments[4] if len(arguments) > 4 else 'pov'
simplify = len(arguments) > 5 and arguments[5] == 'simple'
scene = bpy.context.scene
camera = scene.camera
if recorded_name:
    camera = scene.objects.get(recorded_name)
    if camera is None or camera.type != 'CAMERA':
        raise ValueError('Recorded camera is missing: ' + arguments[3])
    # Modify only this disposable render process, preserving the user's marker bindings.
    for marker in scene.timeline_markers:
        marker.camera = None
    scene.camera = camera
scene.frame_start, scene.frame_end = int(start), int(end)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.background_type = 'WORLD'
# Keep the scene's background and color transform shared with the live POV.
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x=scene.render.pixel_aspect_y=1
if hasattr(scene.render.image_settings, 'media_type'):
    scene.render.image_settings.media_type = 'VIDEO'
else:
    scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = output
saved_visibility=[]
if simplify:
    for ob in scene.objects:
        if ob.get('previs_ai_hide') or ob.get('previs_ai_show'):
            saved_visibility.append((ob,ob.hide_render,ob.hide_viewport));ob.hide_render=bool(ob.get('previs_ai_hide'));ob.hide_viewport=bool(ob.get('previs_ai_hide'))
try:
    if mode!='spatial':bpy.ops.render.render(animation=True)
finally:
    for ob,hidden,viewport in saved_visibility:ob.hide_render=hidden;ob.hide_viewport=viewport
if mode!='spatial':print('EXPORTED', output, scene.frame_start, scene.frame_end)

if mode in ('overview','spatial'):
    # The POV file above is deliberately retained as the clean source deliverable.
    root = Path(__file__).resolve().parents[1]
    import sys as _sys
    _sys.path.insert(0, str(root / 'addon'))
    from whitebox_overview import OverviewRig, read_zones
    _sys.path.insert(0, str(root / 'scripts'))
    from compose_overview import create_legend, compose, write_zones_json, write_reference_text, create_board, compose_board
    zones = read_zones(scene)
    overview = str(Path(output).with_name(Path(output).stem + '_overview.mp4'))
    combined = str(Path(output).with_name(Path(output).stem + '_combined.mp4'))
    zones_json = str(Path(output).with_name(Path(output).stem + '_zones.json'))
    legend = str(Path(output).with_name(Path(output).stem + '_legend.png'))
    rig = OverviewRig(scene)
    overview_camera = getattr(rig, 'camera', None) or getattr(rig, 'overview_camera', None)
    if overview_camera is None:
        raise RuntimeError('OverviewRig did not expose an overview camera')
    overview_scene = rig.scene
    overview_scene.render.resolution_x, overview_scene.render.resolution_y = 1280, 720
    overview_scene.render.resolution_percentage = 100
    overview_scene.render.pixel_aspect_x=overview_scene.render.pixel_aspect_y=1
    overview_scene.render.fps, overview_scene.render.fps_base = scene.render.fps, scene.render.fps_base
    overview_scene.frame_start, overview_scene.frame_end = int(start), int(end)
    if hasattr(overview_scene.render.image_settings, 'media_type'):
        overview_scene.render.image_settings.media_type = 'VIDEO'
    else:
        overview_scene.render.image_settings.file_format = 'FFMPEG'
    overview_scene.render.ffmpeg.format = 'MPEG4'; overview_scene.render.ffmpeg.codec = 'H264'; overview_scene.render.ffmpeg.audio_codec = 'NONE'
    # Bake observer helpers before rendering. Rendering a second shared scene
    # from frame-change handlers can otherwise read a stale source-camera graph.
    baked=[]
    for f in range(int(start),int(end)+1):
        scene.frame_set(f)
        rig.update(camera, None)
        baked.append((f,rig.camera_model.matrix_world.copy(),rig.camera.matrix_world.copy(),
                      [[tuple(p.co) for p in ob.data.splines[0].points] for ob in rig.frustum_objects]))
    previous={}
    def bake_transform(ob,matrix,f):
        loc,quat,scale=matrix.decompose()
        if ob.name in previous and previous[ob.name].dot(quat)<0:quat.negate()
        previous[ob.name]=quat.copy()
        ob.rotation_mode='QUATERNION';ob.location=loc;ob.rotation_quaternion=quat;ob.scale=scale
        for channel in ('location','rotation_quaternion','scale'):ob.keyframe_insert(data_path=channel,frame=f)
    for f,pose,observer,frustum in baked:
        bake_transform(rig.camera_model,pose,f);bake_transform(rig.camera,observer,f)
        for plate in rig.number_plates:
            plate.rotation_quaternion=observer.to_quaternion();plate.keyframe_insert(data_path='rotation_quaternion',frame=f)
        for ob,points in zip(rig.frustum_objects,frustum):
            for pt,value in zip(ob.data.splines[0].points,points):
                pt.co=value;pt.keyframe_insert(data_path='co',frame=f)
    # Export evidence records the exact first/last helper transforms.
    import json as _json
    Path(output).with_name(Path(output).stem+'_sync.json').write_text(_json.dumps({
        'frame_start':int(start),'frame_end':int(end),
        'camera_start':list(baked[0][1].translation),'camera_end':list(baked[-1][1].translation),
        'observer_start':list(baked[0][2].translation),'observer_end':list(baked[-1][2].translation),
        'method':'baked helper transforms and lens frustum geometry, same frame range as POV'},indent=2), encoding='utf-8')
    old_scene = bpy.context.window.scene if bpy.context.window else None
    try:
        if bpy.context.window:bpy.context.window.scene=overview_scene
        overview_scene.camera=overview_camera;overview_scene.render.filepath=overview
        overview_scene.frame_set(int(start))
        bpy.ops.render.render(animation=True)
    finally:
        if bpy.context.window and old_scene:bpy.context.window.scene=old_scene
    create_legend(zones, legend, scene.unit_settings.scale_length)
    write_zones_json(zones, scene, camera, zones_json, start, end)
    write_reference_text(zones,scene,camera,Path(output).with_name(Path(output).stem+'_reference.txt'),int(start),int(end),simplify)
    # One labelled still for spatial reference; its observer is not the final shot.
    overview_still=Path(output).with_name(Path(output).stem+'_spatial.png')
    overview_scene.render.image_settings.media_type='IMAGE';overview_scene.render.image_settings.file_format='PNG'
    overview_scene.frame_set(int(start))
    overview_scene.render.filepath=str(overview_still)
    try:
        if bpy.context.window:bpy.context.window.scene=overview_scene
        bpy.ops.render.render(write_still=True)
    finally:
        if bpy.context.window and old_scene:bpy.context.window.scene=old_scene
    create_board(legend,overview_still,Path(output).with_name(Path(output).stem+'_board.png'))
    board_movie=str(Path(output).with_name(Path(output).stem+'_board.mp4'))
    compose_board(scene,overview,str(Path(output).with_name(Path(output).stem+'_board.png')),board_movie,int(start),int(end))
    if mode=='overview':compose(scene,output,board_movie,combined,int(start),int(end))
    print('EXPORTED_SPATIAL',overview,board_movie,zones_json)
    if mode=='overview':print('EXPORTED_COMBINED',combined)
