# Source availability

The project and its official source distribution are GPL-3.0-or-later software. The
0.8.0-preview.3 Lite/Pro packages use the same source and launcher; Pro is an
offline entitlement inside that source, not a separate closed binary.

The source package includes the application Python, Blender add-on, web
client, licensing runtime, export policy, tests, documentation, dependency
metadata, and the `LICENSE` file. `MANIFEST.sha256.json` records SHA-256
checksums for the files in each generated package.

The package deliberately excludes user projects, takes, runtime connection
tokens, production license stock, private or encrypted private keys, and the
developer-only `tools/license_issuer` utilities. These exclusions protect
user data and signing secrets; they do not remove the corresponding DKYJ
application source covered by GPL-3.0-or-later.

The platform ZIPs are source-and-launcher distributions. They still require
the separately licensed Blender installation and resolve Python dependencies
from `requirements.txt` during setup. A recipient who receives a GPL-covered
copy may inspect, modify, and redistribute the corresponding source under the
GPL terms. Repository visibility or a paid Pro entitlement does not withdraw
those rights from earlier recipients.
