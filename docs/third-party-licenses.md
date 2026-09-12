# Third-party notices

DKYJ Director is distributed under the GNU General Public License v3.0. The
application uses the following Python packages through the installation
environment. They are installed from their upstream distributions and are not
copied into the source or platform ZIPs.

| Package | Observed development environment | License | Upstream |
| --- | --- | --- | --- |
| `cryptography` | 50.0.1 | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| `Pillow` | 12.3.0 | MIT-CMU | https://github.com/python-pillow/Pillow |
| `qrcode` | 8.2 | BSD | https://github.com/lincolnloop/python-qrcode |
| `mcp` (optional agent integration) | 1.29.1 | MIT | https://github.com/modelcontextprotocol/python-sdk |
| `blender-mcp` (optional Blender integration) | 1.9.1 | MIT | https://github.com/ahujasid/blender-mcp |

Versions above record the local audit environment and may change when the
version ranges in `requirements.txt` are resolved. The installed package
metadata and upstream license files are the authoritative notices for the
resolved version. A release build must not silently vendor or modify these
packages.

VirtuCamera and other third-party commercial plugins are not redistributed by
this project. Users install them separately under their own license terms.
