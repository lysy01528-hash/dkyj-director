# DKYJ Director

<img src=".github/assets/dkyj-director-hand-eye.png" width="220" alt="DKYJ Director hand-drawn logo">

**A local camera previs desk for Blender.**
大开眼界导演台 — build simple scenes, block action, and record camera moves from your phone.

English | [简体中文](INSTALL.zh-CN.md)

![Steamship spatial previs](.github/assets/steamship-board.png)

**0.8.0-preview.3 — Lite / Pro public preview.**

One package per platform, with Lite and Pro using the same application. Lite saves **3 scenes per project**; additional scenes can be edited temporarily and saved after manually deleting an old scene. Touch, phone orientation and keyboard recording remain available. Gamepad preview is free; gamepad recording requires Pro. Lite exports contain a Preview watermark; Pro exports are clean.

[Lite / Pro guide](docs/licensing.md) · [Offline delivery status](docs/afdian-delivery.md) · [Corresponding source](docs/source-availability.md)

This build includes the production v1 verification key and accepts valid Pro activation codes offline. The Afdian purchase URL and automated order delivery are not configured or verified yet.

[Included examples: Room + Steamship](samples/README.md) · [Release notes](docs/release-notes.md)

## What it does

DKYJ Director connects a Blender scene on your computer to a browser viewfinder. Use simple colored characters and editable keyframes to plan a shot, then record the camera with touch movement and phone orientation.

- Live camera view plus a synchronized spatial overview.
- Color-coded spaces, approximate metric dimensions, a camera model, frustum and path.
- Saved projects: reopen models without regenerating them, or copy a scene into an independent variation.
- Camera recording with position, rotation and focal-length keyframes.
- Xbox Series X|S and PS5 DualSense controller camera control is connected in the current source; choose the compact Xbox / PS5 profile beside the controller button. See [controller camera control](docs/gamepad.md) for the mapping and tested limits. PS5 hardware is not yet verified.
- Clean POV video, overview video, combined video, spatial JSON, reference text and a scene board.
- Optional AI scene editing through your own local MCP-capable agent.

## Can I run it on GitHub?

**Download it from GitHub and run it on your computer.** The repository homepage provides documentation and links to installation bundles with their corresponding source; it is not a hosted Blender application.

[GitHub Pages hosts static HTML, CSS and JavaScript](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). It can host a presentation or prerecorded demo, but cannot run this Blender/Python/GPU backend. Publishing the `web/` folder alone does not provide a working director desk. No public relay or hosted rendering service is included.

## Quick start

Choose the **macOS** or **Windows** ZIP. These are source-and-launcher installation bundles, not standalone EXE/DMG apps; Blender and Python are installed separately. Windows: follow [Windows setup](docs/windows.md), double-click **Install DKYJ Director.cmd**, then **Launch DKYJ Director.cmd**. The commands below use macOS paths; on Windows use `.venv\Scripts\python.exe`.

Desktop: **macOS + Safari / Windows 11 x64 + Edge**. Mobile support: **iPhone Safari only**. The macOS launcher explicitly opens Safari. Local backend checks use **macOS / Apple Silicon and Blender 5.2.1 LTS**; install **Python 3.11+**. See [release checks](docs/release-check.md) for tested coverage and remaining device checks. Windows paths, LAN selection, Chinese fonts and UTF-8 handling are implemented and branch-tested; native Windows GPU/phone validation remains pending. Linux is not a supported release target.

1. Download [Blender](https://www.blender.org/download/) (macOS Apple Silicon on M-series Macs; install in Applications) and [Python 3.11+](https://www.python.org/downloads/macos/) from their official sites.
2. Download the [macOS or Windows installation ZIP from Releases](https://github.com/wangjiake666/dkyj-director/releases/tag/v0.8.0-preview.3), then extract it. The repository’s **Code → Download ZIP** contains the guide and nested installer ZIPs; extract the matching ZIP in `downloads/` before setup.
3. Open a terminal in the extracted directory and run:

```sh
python3 scripts/setup.py
.venv/bin/python scripts/launch.py
```

On macOS, you can also open **Launch DKYJ Director.command**. If a source download has lost executable permissions, run `chmod +x *.command` first. First setup installs Python dependencies, generates the bundled room and steamship scenes once, and installs the local Blender addon. Run setup again after moving the repository. For a custom Blender executable, use `python3 scripts/setup.py --blender /path/to/blender` and set `DKYJ_BLENDER` when launching.

Keep Blender and a visible 3D viewport open. The macOS launcher opens Apple Safari and prints the phone URL. Connect the phone to the same Wi-Fi and open that URL in Safari. Connection details and a QR code are stored in `runtime/`; do not share that directory.

The current application controls and sample scene labels are primarily Chinese. This README and the agent guide provide English onboarding; [the Chinese manual](INSTALL.zh-CN.md) includes the detailed control descriptions.

## Welcome and creative conversation

The welcome screen includes an expandable first-use guide with Blender/Python download links and Blender MCP installation steps. It asks four questions: the scene, characters/count, action and timing, and camera intent. Review the brief, choose an existing model, then submit it as a durable local task. Draft answers stay in that browser until submission.

Your connected agent can read the task, create an independent scene variation, ask follow-up questions, report progress and save the result. The UI distinguishes waiting, working, needs-input, ready and failed. A queued description is never shown as generated geometry.

To use this workflow, connect **both** the optional DKYJ Director MCP server (task/project management) and Blender MCP (scene editing). Install the optional dependency and print a configuration entry:

```sh
.venv/bin/python -m pip install -r requirements-agent.txt
python3 scripts/agent_config.py
```

Merge that entry into your own agent's MCP configuration alongside Blender MCP. Then ask the agent to execute the next DKYJ task. MCP connection alone does not automatically wake every agent application; a conversation turn must initiate work. No built-in LLM, API key or paid model call is required by this repository.

The phone welcome screen and viewfinder retain DKYJ / 大开眼界 branding. See [Trial guide](docs/trial-guide.md).

## Bring your own agent

The core director works without an AI service or paid phone app. AI scene editing requires a separate **Blender MCP addon + MCP server**, configured in an agent that supports local MCP tools. Cloud-only chat cannot reach your computer automatically.

```text
Your local agent → Blender MCP → Blender scene
                                     ↕
                              DKYJ Director
                                     ↕
                           Desktop / phone browser
```

Follow [Agent setup](docs/agent-setup.md), then give your agent [AGENT_GUIDE.md](AGENT_GUIDE.md). The agent should first confirm it can read the active Blender scene. For project management through the supplied CLI, it also needs local shell access. The project description field stores a brief; it does not call a model on its own. Welcome-screen tasks are handed to the connected external agent through the optional DKYJ MCP server.

Example prompt:

> Read AGENT_GUIDE.md and check the local DKYJ Director and Blender MCP connection. List the saved projects. Reuse the steamship model in a new independent project: a character runs from the cabin onto the deck while a plane passes overhead. Preserve editable keyframes, keep the original project, save the new version, and report what you verified.

## Record a shot

1. Select `Camera_Phone`. Set the timeline, lens and starting position. `Camera_Demo` is a prerecorded example camera.
2. Use the left joystick to move, +/− to rise or descend, and drag the image to look around. Desktop controls use WASD/QE. Phone walking does not track translation.
3. Start recording. The app creates a separate `Camera_Take_*` and plays the character animation while recording your camera.
4. Stop recording and scrub the timeline to review. Live input is held after stopping; resume viewfinding explicitly to avoid changing the recorded take.
5. Export the clean POV or the reference suite. Export uses the recorded camera even if you later select a live view. Rehearsal alone does not record a take.

For phone orientation, use the launcher's HTTPS link. First install the project-local certificate profile on the iPhone, enable its trust in Settings, then grant motion permission in Safari. Calibrate while holding the phone naturally. Setup never changes device trust automatically. See the [Chinese certificate walkthrough](README.zh-CN.md#iphone-体感转向).

## Reuse scenes

Open the project button in the top bar. Save the current scene, open an existing project, edit its brief, or create a variation from the current model or another saved project. Switching saves the scene being left; copying creates independent scene, mesh and action data. Recording/export must finish before a switch.

Projects live in `projects/library/<id>/scene.blend`, with one previous-file backup. The catalog is `projects/index.json`. Restart restores the last saved active project. Use the project's **Save current project** action before closing Blender; ordinary Ctrl-S is not a substitute for saving to the project library.

The interface supports one operator and a shared camera. More open scene projects consume more Blender memory. Procedural examples are generated at first setup, never regenerated simply to switch projects.

## Exports

| File | Purpose |
| --- | --- |
| POV MP4 | 1280 × 720 H.264, no audio or interface overlays |
| Overview MP4 | Pure observer view, 1280 × 720, 16:9 |
| Spatial board MP4 | Descriptions + synchronized overview, 1920 × 1080, 16:9 |
| Combined MP4 | 1920 × 2160; two equally sized 1920 × 1080 panels, each 16:9 |
| JSON | Space sizes, subjects, action beats and sampled camera data |
| TXT | Shot reference notes and color-to-subject mapping |
| PNG | Overview board with space descriptions and dimensions |

The optional simplified-character export hides tagged limbs in the clean POV while keeping source animation editable. The clean shot communicates composition and motion; the board explains spatial relationships. These files are not a guaranteed upload schema or generation result for an AI video platform. [Seedance reference notes](docs/seedance-2.5-reference.md) document the source material used.

## Development and limits

```sh
python3 scripts/doctor.py
python3 -m compileall -q addon scripts tests
node scripts/test_web_controls.cjs
blender --background --factory-startup --python-exit-code 1 --python tests/test_projects.py
blender --background --factory-startup --python-exit-code 1 --python scripts/test_recorded_export.py
```

The current sample previews at approximately 6–7 fps on the tested machine; export uses the scene frame rate. Project independence, save/reload, recorded-camera ownership and actual three-view renders have been checked. There is no cross-device phone test matrix or paid AI generation validation. Use this as a local LAN tool, not a public Internet service.

See [Project API](docs/project-api.md), [Architecture](docs/architecture.md), [Changelog](CHANGELOG.md), and [Development log](docs/development-log.md). Supporting technical notes currently include Chinese documentation.

## Publish and license

Run `python3 scripts/package_release.py --platform all` to generate the allowlisted source folder and ZIP. The package excludes private projects, certificates, pairing tokens, takes, QA output, virtual environments and third-party addons. See [Publishing on GitHub](docs/github-publishing.md).

Source and procedural examples are licensed under **GPL-3.0-or-later**. See [LICENSE](LICENSE). Blender, Python and optional Blender MCP remain separate dependencies with their own licenses. They are not bundled with this release.

## Collaboration

For collaborations and project inquiries:

- Douyin / 抖音: **王夹克**
- WeChat Official Account / 微信公众号: **大开眼界AI**
- Email: **[826701673@qq.com](mailto:826701673@qq.com)**

These contacts are also visible in the welcome screen and the viewfinder’s Contact menu on desktop and phone.

### Separate 16:9 exports

Use the camera export for clean POV, the spatial export for the labelled board and pure observer video, or the reference suite for all files plus the stacked video. Spatial-only export skips POV and combined rendering. [Exact formats](docs/export-formats.md).
