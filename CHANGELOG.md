# Changelog

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
