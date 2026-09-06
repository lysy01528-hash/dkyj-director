"""Shared IPv4 selection for the server, phone URL and TLS certificate."""
import ipaddress
import os
import re
import socket
import subprocess
import sys


def usable_ipv4(value):
    try:
        ip = ipaddress.ip_address(value)
        return ip.version == 4 and any(ip in ipaddress.ip_network(net) for net in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))
    except ValueError:
        return False


def interface_addresses(output, platform):
    if platform == 'win32':
        lines = [line for line in output.splitlines() if 'IPv4' in line]
    else:
        lines = [line for line in output.splitlines() if line.strip().startswith('inet ')]
    return list(dict.fromkeys(ip for line in lines for ip in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)[:1] if usable_ipv4(ip)))


def lan_addresses():
    override = os.environ.get('DKYJ_LAN_IP', '').strip()
    if override:
        if not usable_ipv4(override):
            raise RuntimeError('DKYJ_LAN_IP must be a private LAN IPv4 address, e.g. 192.168.1.10')
        return [override]
    found = []
    # UDP connect chooses the default route without sending a packet.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(('8.8.8.8', 80))
            found.append(probe.getsockname()[0])
    except OSError:
        pass
    command = ['ipconfig'] if sys.platform == 'win32' else ['/sbin/ifconfig']
    try:
        output = subprocess.check_output(command, timeout=5).decode(errors='replace')
        found.extend(interface_addresses(output, sys.platform))
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        found.extend(item[4][0] for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET))
    except OSError:
        pass
    return list(dict.fromkeys(ip for ip in found if usable_ipv4(ip)))


def lan_ip():
    return next(iter(lan_addresses()), '127.0.0.1')
