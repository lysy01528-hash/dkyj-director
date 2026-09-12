# Changelog

## 0.8.0-preview.3 — Public download preview, 2026-09-12

- Keep the existing GitHub repository name and URL; the current tree becomes a bilingual download and documentation hub.
- Publish shared Lite/Pro macOS and Windows source-and-launcher bundles with the production v1 verification key and SHA-256 manifests.
- Include Xbox / PS5 profiles, elevation and pitch, three saved Lite scenes per project, Pro controller recording, Preview export watermarks and camera-deletion recovery.
- Keep the room and steamship examples, phone pairing, Blender/MCP onboarding and separate or combined 16:9 views.
- Preserve corresponding GPL application source in each bundle; seller tools, credentials, stock and personal projects stay out of public distribution.
- Afdian automatic purchase/delivery, native Windows GPU, iPhone and PS5 hardware acceptance remain pending.

## 0.8.0-preview.2 — Local production activation readiness

- Embed the author-approved production v1 public key; signed Pro codes now activate offline.
- Preserve preview.1 packages and rebuild both platforms with the same verifier key.
- Verify 10 issued codes, fresh-process restart, wrong-code preservation and rejection of unrelated signing keys.
- Make client-package licensing tests independent of excluded developer issuer tools.
- Afdian purchase/delivery and GitHub publication are still pending.


## 0.8.0-preview.1 — Local build, 2026-09-12

- Lite and Pro now share one macOS/Windows source-and-launcher package. The production Pro key/product are intentionally unconfigured pending owner setup and real delivery acceptance.
- Added strict Ed25519 offline license validation, per-user atomic storage, masked license status, secure activation transport and a compact version panel. The developer issuer stays outside user packages.
- Added project-owned scenes: Lite saves three, excess scenes remain temporary until a user manually deletes a saved scene. Existing projects migrate with an index backup; deletion retains a trash copy. Removed Scene wrappers no longer break the new catalog.
- Kept gamepad camera preview free; Pro gates gamepad recording. Manual recording remains available with Preview watermarks. Added controller ownership, neutral shutdown and heartbeat expiry without changing joystick mathematics.
- Added an isolated built-in demo process for controller trial recording. Formal project writes and demo export are denied.
- Applied Preview marking to POV, overview, board, combined video, stills and reference metadata. Real Blender short exports passed all three modes, including noninteger FPS and Pro passthrough.
- Added CLI/MCP scene commands that wait for the backend project event, and updated source-availability and dependency notices.
- This is a local development build. Real Afdian purchase/delivery, production activation, Windows/iPhone and DualSense hardware acceptance are not complete. Repository privacy/download-site migration has not run.

## Controller development baseline (previously unreleased)

- Added Xbox Series X|S controller camera control to the web viewfinder: left stick movement, right stick turn/pitch, LT/RT elevation and LB/RB focal length.
- Added the four screen controls for elevation and pitch, the waiting/ready/active connection states and the world-coordinate camera Z display. Recording remains on the existing web buttons; controller A/B are not part of this version.
- Added focus-loss, background-pause and disconnect/reconnect centering behavior, with same-page arbitration against phone orientation, keyboard, dragging and screen controls. This baseline originally had no backend lock; 0.8 adds controller ownership and expiry.
- Passed 45 production `web/gamepad.js` and `app.js` behavior checks with at most one concurrent control request. Synthetic input using the production mapping recorded and replayed a 41-frame, 1.708-second Take in Blender 5.2.1 LTS, including elevation, position, pitch and focal length, and produced a 1280×720 MP4.
- Fixed timeline `frame_set` restoring old focal-length keyframes over live zoom during recording; live zoom now enters the Take. Previous Mac Safari 18.6 hardware probing read both sticks and LT/RT/LB/RB; this version's hardware recording in Blender, Windows Edge and iPhone Safari remain unverified.
- See [Xbox / PS5 controller camera control](docs/gamepad.md).
- Added a compact Xbox / PS5 profile selector beside the controller button. Xbox remains the default; the selected value is stored in the browser and invalid values fall back to Xbox.
- Added PS5 standard-layout mapping: L2/R2 for lowering/raising and L1/R1 for focal length. Only `mapping: "standard"` is accepted; PS5 hardware has not been tested; the touchpad, face buttons and vibration are not used.
- Switching profiles pauses the current controller, sends zero input, resets centering protection and requires clicking controller enable again. Production tests cover profile memory, fallback, PS5 mapping, labels, non-standard rejection and re-centering; no PS5 hardware is available for real-device verification.

## 0.7.0-preview.5 — 2026-09-09

- Recover the phone camera after externally deleting active takes; interrupt a deleted recording safely without keying another camera.
- Validate Scene/Object identities, discard deleted project caches and rebuild stale overview rigs; make helper cleanup repeatable.
- Release GPU resources before undo/redo/file loading and prevent state-refresh exceptions from terminating the web timer.
- Keep the green export download button on the neutral gray interface.
- Verified in Blender 5.2.1 on macOS: eight deletion regressions, seven overview cleanup cases, native GPU/HTTP recovery including Undo, project reload and recorded-export regressions.
- Reproduction, upgrade instructions and validation limits: [deleted-camera recovery](docs/fixes/deleted-camera-recovery.md).


## 0.7.0-preview.4 — 2026-09-07

- Phone pairing links open the viewfinder directly and select Camera_Phone once per project; legacy iPhone links also select the phone camera.
- Live control copies use Camera_Phone; animated source cameras and recorded takes remain intact.
- Recorded camera motion and export ownership regression checks pass.


## 0.7.0-preview.3 — 2026-09-07

- Added prominent phone-pairing buttons to the desktop header and welcome page, with local QR codes, copyable links and iPhone Safari setup instructions.
- HTTP and HTTPS QR codes are generated locally and require the active pairing token; no external QR service is used.
- Changed interface colors to neutral grayscale while preserving scene, actor and exported video colors.
- Corrected the isolated Windows CI test user-home environment.
- Excluded proxy benchmark addresses and interface broadcast addresses from phone pairing links.


## 0.7.0-preview.2 — 2026-09-06

- First public preview distribution with separate macOS and Windows bundles.
- Includes curated room and steamship demonstration videos, scene generators and bilingual example instructions.
- Uses an explicit file allowlist; local project libraries, recordings, credentials and QA artifacts are excluded.
- Preserves current camera recording, spatial exports, MCP onboarding and project-switching behavior.
- Native Windows GPU and iPhone acceptance checks remain pending as documented.

## 0.7.0-preview.1 — 2026-09-06 · Not published

- Separate macOS and Windows ZIP installation bundles with platform-specific launchers.
- Windows Blender discovery, saved custom executable, virtualenv paths, UTF-8 data and Chinese font support.
- Shared LAN address detection and optional DKYJ_LAN_IP for server and iPhone TLS.
- Windows desktop opens Edge; mobile support remains iPhone Safari only.
- Added Windows guide and platform branch tests; configured three-OS CI. Native Windows GPU/phone validation is pending.

## 0.6.0-preview.4 — 2026-09-06 · Not published

- Added Douyin, WeChat Official Account and email contacts to desktop/mobile welcome and viewfinder Contact menu.
- Updated bilingual README and release package.

## 0.6.0-preview.3 — 2026-09-06 · Not published

- Added first-use Blender/Python download and Blender MCP setup guidance in the welcome screen.
- macOS launcher now explicitly opens Apple Safari; bilingual documentation uses Safari for Mac and iPhone.
- Replaced the portrait logo with a transparent hand-and-eye design.
- Rechecked project persistence, brief replies, camera ownership and export artifacts.
- Added release-check record with actual coverage and pending Safari device validation.
- Refreshed official Seedance references and prepared a clean source distribution.

## 0.6.0-preview.2 — 2026-09-06 · Not published

- Separate 16:9 POV and spatial-board export buttons.
- Labelled spatial board: 1920×1080; clean POV/observer: 1280×720.
- Combined video: 1920×2160, with two undistorted 1920×1080 panels.
- Added hand-drawn transparent DKYJ Director logo to bilingual README.
- Added export artifact validation, format documentation and logo generation record.

## 0.6.0-preview.1 — 2026-09-06 · Not published

- Added branded desktop/mobile welcome and four-step creative conversation.
- Durable task queue, follow-up replies and truthful waiting/working/ready statuses.
- Optional DKYJ stdio MCP tools for external agents; Blender MCP remains the scene editor.
- Added configuration generator, brief persistence tests and trial guide.
- Fixed project submission pending guard when revision is zero.


## 0.5.1 — 2026-09-06

- English-first repository README with a complete Chinese manual.
- Agent onboarding guide, local connection doctor and English macOS launcher.
- Clarified local runtime versus GitHub Pages hosting.
- Added collaboration contact: 826701673@qq.com.


## 0.5.0 — 2026-09-06

- 名称改为 DKYJ Director · 大开眼界导演台。
- 新增网页项目库：保存、自动保存后切换、复用模型创建独立项目、编辑描述。
- 新增本地项目 CLI 与数据接口；重启恢复活动工程。
- 独立存储 Scene 与依赖，修正 Blender 自动重名后的角色和录制摄影机引用。
- 去除开发机固定目录，增加安装入口、可选 MCP、依赖清单、许可证及源码打包脚本。

## 0.4.0 — 2026-09-06

- 蒸汽小船示例：角色出舱、甲板停步、飞机掠过；陈设与关键帧保留。
- 干净桌面总览、分区尺度、带方向的摄影机视锥、轻微跟随观察机位。
- 同步三路视频、JSON、TXT、说明 PNG；摄影机模型轨迹预先烘焙。
- 可选简化人物导出；整理 Seedance 白模参考材料。

## 0.3.0 — 2026-09-06

- 新增空间分区总览及参考套件导出。

## 0.2.0 — 2026-09-06

- 修正导出未绑定录制镜头的问题。
- 停止录制后暂停体感与触控，恢复取景使用独立 Live 机位。

## 0.1.0 — 2026-09-06

- 本地 Blender 网页取景、iPhone 触控和体感转向、人物动作及可编辑关键帧。
