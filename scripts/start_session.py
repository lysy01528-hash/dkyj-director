"""Prepare a dedicated Blender window for MCP and phone pairing."""
import json
import os
from pathlib import Path

import bpy

root = Path(__file__).resolve().parents[1]

def prepare():
    scene = bpy.context.scene
    if 'whitebox_webcam' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='whitebox_webcam')
    # MCP is an optional bridge; the web director works without it.
    import addon_utils
    available={m.__name__ for m in addon_utils.modules()}
    if 'blender_mcp' in available:
        if 'blender_mcp' not in bpy.context.preferences.addons:bpy.ops.preferences.addon_enable(module='blender_mcp')
        bpy.context.preferences.addons['blender_mcp'].preferences.telemetry_consent=False
        scene.blendermcp_port=9876
        if not getattr(scene,'blendermcp_server_running',False):bpy.ops.blendermcp.start_server()
    if os.environ.get('PREVIS_RESUME') != '1':
        camera = bpy.data.objects.get('Camera_Phone')
        if camera:
            scene.camera = camera
        scene.frame_set(1)
    started = False
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'SOLID'
                area.spaces.active.shading.color_type = 'MATERIAL'
                area.spaces.active.overlay.show_overlays = False
                area.spaces.active.show_region_ui = True
                if not started:
                    region = next(r for r in area.regions if r.type == 'WINDOW')
                    with bpy.context.temp_override(window=window, area=area, region=region):
                        started = bpy.ops.wbvcam.start() == {'FINISHED'}
    report = {
        'file': bpy.data.filepath,
        'blender': bpy.app.version_string,
        'mcp_running': getattr(scene,'blendermcp_server_running',False),
        'mcp_port': getattr(scene,'blendermcp_port',None),
        'webcam_started': started,
        'camera': scene.camera.name if scene.camera else None,
        'phone_paired': False,
    }
    (root/'qa').mkdir(exist_ok=True)
    (root / 'qa/session.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    (root / 'qa/launch.json').write_text(json.dumps({'pid': os.getpid()}), encoding='utf-8')
    print('PREVIS_SESSION', json.dumps(report, ensure_ascii=False), flush=True)
    return None

bpy.app.timers.register(prepare, first_interval=1.0)
