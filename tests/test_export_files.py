"""Blender regression: independent spatial download and missing-file rejection."""
import importlib.util,tempfile
from pathlib import Path
from types import SimpleNamespace
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('webcam_test',root/'addon/whitebox_webcam.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as d:
    module.TAKES=Path(d)
    for suffix in ['_board.mp4','_overview.mp4','_zones.json','_reference.txt','_board.png']:(Path(d)/('sample'+suffix)).write_bytes(b'fixture')
    s=module.Viewfinder.__new__(module.Viewfinder);s.export_log=None;s.export_name='sample.mp4';s.export_camera_name='Take';s.export_mode='spatial';s.export_process=SimpleNamespace(returncode=0);s.token='test';s.downloads=set()
    s.finish_export();assert s.export_state['status']=='done',s.export_state
    assert 'sample_board.mp4' in s.export_state['url'];assert len(s.export_state['files'])==5
    assert not (Path(d)/'sample.mp4').exists()
    (Path(d)/'sample_board.mp4').unlink();s.export_process=SimpleNamespace(returncode=0);s.finish_export();assert s.export_state['status']=='error'
print('EXPORT_FILES_OK spatial without POV; missing primary rejected')
