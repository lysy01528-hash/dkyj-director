"""Platform branch checks; Windows execution is also configured in CI."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import platform_paths as paths
import network_utils as network


class PlatformTests(unittest.TestCase):
    def test_windows_unicode_and_multiple_blenders(self):
        with tempfile.TemporaryDirectory(prefix='dkyj 场景 ') as tmp:
            root=Path(tmp)
            for version in ['5.2','5.10']:
                file=root/('Blender Foundation/Blender '+version)/'blender.exe'
                file.parent.mkdir(parents=True);file.touch()
            with patch.object(paths, 'ROOT', root), patch.object(paths.sys, 'platform', 'win32'), patch.dict(os.environ, {'PROGRAMFILES':tmp, 'LOCALAPPDATA':tmp}, clear=True), patch.object(paths.shutil, 'which', return_value=None):
                self.assertIn('Blender 5.10', paths.blender_binary())
                self.assertEqual(paths.project_python(root), root/'.venv/Scripts/python.exe')
    def test_invalid_explicit_blender_does_not_silently_fallback(self):
        with patch.dict(os.environ, {'DKYJ_BLENDER':'/nonexistent/dkyj-blender'}):
            with self.assertRaises(RuntimeError):paths.blender_binary()
    def test_windows_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            font=Path(tmp)/'Fonts/msyh.ttc';font.parent.mkdir();font.touch()
            with patch.dict(os.environ, {'WINDIR':tmp, 'DKYJ_FONT':''}), patch.object(Path, 'is_file', lambda candidate: str(candidate) == str(font)):
                self.assertEqual(paths.chinese_font(), str(font))
    def test_localized_ipconfig_excludes_gateway_and_linklocal(self):
        text='IPv4 地址 . . : 192.168.31.5(首选)\n默认网关 : 192.168.31.1\nIPv4 Address: 169.254.8.2\nIPv4 Address: 10.0.0.3'
        self.assertEqual(network.interface_addresses(text,'win32'), ['192.168.31.5','10.0.0.3'])
    def test_mac_addresses(self):
        text='en0: flags\n\tinet 192.168.1.8 netmask 0xffffff00\n\tinet 127.0.0.1\n\tinet6 fe80::1'
        self.assertEqual(network.interface_addresses(text,'darwin'),['192.168.1.8'])
    def test_offline_fallback_and_explicit_ip(self):
        with patch.dict(os.environ, {'DKYJ_LAN_IP':''}), patch.object(network.socket,'socket',side_effect=OSError), patch.object(network.socket,'getaddrinfo',side_effect=OSError), patch.object(network.subprocess,'check_output',side_effect=OSError):
            self.assertEqual(network.lan_ip(),'127.0.0.1')
        with patch.dict(os.environ, {'DKYJ_LAN_IP':'192.168.2.8'}):self.assertEqual(network.lan_ip(),'192.168.2.8')
        with patch.dict(os.environ, {'DKYJ_LAN_IP':'8.8.8.8'}):
            with self.assertRaises(RuntimeError):network.lan_ip()


if __name__ == '__main__':unittest.main()
