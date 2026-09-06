"""Create project-only TLS files; does not install or trust a certificate on any device."""
import datetime
import ipaddress
import json
import plistlib
import socket
import subprocess
import uuid
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

root = Path(__file__).resolve().parents[1]
directory = root / 'runtime/tls'
directory.mkdir(parents=True, exist_ok=True)
from network_utils import lan_addresses
addresses = ['127.0.0.1'] + lan_addresses()
now = datetime.datetime.now(datetime.timezone.utc)
# Reuse this project's CA so renewing the leaf or changing LAN IP does not require re-trusting it.
existing_ca = directory / 'ca.pem'
existing_key = directory / 'ca-key.pem'
ca = None
if existing_ca.exists() and existing_key.exists():
    candidate = x509.load_pem_x509_certificate(existing_ca.read_bytes())
    if candidate.not_valid_after_utc > now + datetime.timedelta(days=31):
        ca = candidate
        ca_key = serialization.load_pem_private_key(existing_key.read_bytes(), password=None)
        subject = ca.subject
if ca is None:
    ca_key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Blender Local Camera — Private LAN')])
    ca = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(ca_key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=5))
          .not_valid_after(now + datetime.timedelta(days=365)).add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
          .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
              data_encipherment=False, key_agreement=False, key_cert_sign=True, crl_sign=True, encipher_only=False, decipher_only=False), True)
          .sign(ca_key, hashes.SHA256()))
server_key = ec.generate_private_key(ec.SECP256R1())
leaf = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Blender Local Camera')]))
        .issuer_name(subject).public_key(server_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5)).not_valid_after(now + datetime.timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), True)
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(x)) for x in addresses]
                       + [x509.DNSName('localhost')]), False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False)
        .sign(ca_key, hashes.SHA256()))
for name, key in [('ca-key.pem', ca_key), ('server-key.pem', server_key)]:
    file = directory / name
    file.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    file.chmod(0o600)
(directory / 'ca.pem').write_bytes(ca.public_bytes(serialization.Encoding.PEM))
(directory / 'server.pem').write_bytes(leaf.public_bytes(serialization.Encoding.PEM) + ca.public_bytes(serialization.Encoding.PEM))
profile = {'PayloadContent': [{
    'PayloadType': 'com.apple.security.root', 'PayloadVersion': 1,
    'PayloadIdentifier': 'local.blender.camera.certificate.' + str(uuid.uuid4()), 'PayloadUUID': str(uuid.uuid4()),
    'PayloadDisplayName': 'Blender Local Camera', 'PayloadContent': ca.public_bytes(serialization.Encoding.DER),
}], 'PayloadType': 'Configuration', 'PayloadVersion': 1,
    'PayloadIdentifier': 'local.blender.camera.profile.' + str(uuid.uuid4()), 'PayloadUUID': str(uuid.uuid4()),
    'PayloadDisplayName': 'Blender Local Camera',
    'PayloadDescription': 'Trust this computer’s local Blender camera HTTPS endpoint. No VPN, proxy, device management or traffic routing is configured.',
    'PayloadOrganization': 'Local Blender Previs', 'PayloadRemovalDisallowed': False}
(directory / 'local-camera.mobileconfig').write_bytes(plistlib.dumps(profile))
(directory / 'info.json').write_text(json.dumps({'addresses': addresses, 'leaf_expires': leaf.not_valid_after_utc.isoformat(),
    'ca_sha256': ca.fingerprint(hashes.SHA256()).hex(), 'installed_on_devices': False}, indent=2), encoding='utf-8')
print('Project-only TLS created for', addresses, '; no system trust settings changed.')
