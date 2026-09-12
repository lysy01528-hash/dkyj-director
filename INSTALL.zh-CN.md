# DKYJ Director

**0.8.0-preview.3 · Lite / Pro 公开预览版**

Lite 与 Pro 共用一个安装包，Mac / Windows 分别提供启动器。Lite 每项目可保存 **3 个场次**；更多场次可以临时编辑，手动删旧场次腾位后保存。触控、手机体感、键盘录制免费，所有 Lite 导出带水印；手柄免费预览，手柄录制及无水印导出由 Pro 解锁。

[版本与授权说明](docs/licensing.md) · [爱发电交付状态](docs/afdian-delivery.md) · [对应源码](docs/source-availability.md)

已配置生产 v1 公钥，当前包可使用作者签发的有效 Pro 码离线激活。正式商品链接与爱发电自动收码链路尚待配置和验收。

案例 · [室内与蒸汽小船案例](samples/README.md) · [版本说明](docs/release-notes.md)


<img src=".github/assets/dkyj-director-hand-eye.png" width="220" alt="DKYJ Director hand-drawn logo">

**大开眼界导演台 · 本地白模运镜预演**

[English](INSTALL.md) | 简体中文

轻量、本地的白模运镜预演台。电脑运行 Blender，手机浏览器取景与运镜；模型、人物动作和摄影机关键帧保存在自己的电脑上。

![蒸汽小船空间预演](.github/assets/steamship-board.png)

- 手机触控平移、体感转向、焦距控制与镜头录制。
- 当前源码已接入 Xbox Series X|S 和 PS5 DualSense 手柄运镜；在手柄按钮旁选择 Xbox / PS5 类型，Xbox 默认。映射、使用步骤和实测边界见 [手柄运镜说明](docs/gamepad.md)。PS5 尚未实体真机验证。
- 同步俯视空间、颜色分区、米制尺寸、摄影机视锥与运动路径。
- 多项目保存和切换，复用已有模型创建独立方案，保存场景描述。
- 导出纯镜头、空间总览和组合视频，以及空间数据与 AI 参考说明。

## 欢迎页与对话式创作

欢迎页“第一次使用”提供 Blender、Python 下载入口和 Blender MCP 安装步骤。打开欢迎页，依次回答：什么场景、几个人／什么角色、动作顺序与时长、镜头怎么走。确认后选择复用模型，点击「交给 Agent」。任务保存到本机，网页显示等待、制作中、需要补充、可预演或失败。

Agent 可通过 **DKYJ Director MCP** 领取任务和操作项目，再通过 **Blender MCP** 修改场景。它可以在网页里追问，你回复后继续制作。完成时必须保存项目并回报验证说明，网页才显示「可预演」。

```sh
.venv/bin/python -m pip install -r requirements-agent.txt
python3 scripts/agent_config.py
```

将输出的 DKYJ 配置加入自己的 Agent，与 Blender MCP 配置并存，然后在 Agent 对话里说「执行下一个 DKYJ 创作任务」。仅连接 MCP 不会自动唤醒所有 Agent；需在 Agent 中启动这次执行。网页不自带模型，不会暗中调用付费接口。

手机端保留大开眼界品牌，欢迎页可进入预演台。完整试用步骤见 [试用指南](docs/trial-guide.md)。请从 [Releases 下载对应系统安装包](https://github.com/wangjiake666/dkyj-director/releases/tag/v0.8.0-preview.3)。

## 在 GitHub 上如何使用？

GitHub 原链接现在作为下载入口。请下载 Releases 里的 Mac / Windows 安装包，内含对应源码；Code → Download ZIP 只有下载说明，不能直接启动。**完整导演台在使用者自己的电脑上运行，不能作为纯静态页面直接部署到 GitHub Pages 后使用。** GitHub Pages 可以放说明、图片或预先渲染的视频；它不能启动本机 Blender、运行 Python 后端或处理 GPU 取景。依据：[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

推荐流程：下载源码 → 在电脑上运行安装脚本 → 启动 Blender 与本地导演台 → 可选接入自己的 Agent → 手机打开同一 Wi-Fi 下的本地取景页 → 录镜头并导出。

## 用自己的 Agent

可以，但 Agent 必须支持**本地 MCP 工具调用**；如果还要直接管理项目文件，需要本地终端或文件权限。纯云端聊天窗口不能自动访问你的 localhost。

本项目与 Blender MCP 是两个独立组件：导演台负责取景、录制、项目管理和导出，MCP 负责让 Agent 修改 Blender。先安装并启动本项目，再按 [Agent 接入说明](docs/agent-setup.md) 配置 Blender MCP。让 Agent 先读取场景并确认当前工程，再创建简模或动作。网页描述框仅保存简报，不会自行调用模型。

可直接复制给 Agent：

> 请阅读这个仓库的 AGENT_GUIDE.md，检查 DKYJ Director 与 Blender MCP 的连接。先列出已保存的项目，复用蒸汽小船模型创建一个独立方案。人物从船舱跑上甲板，飞机从头顶掠过；保留可编辑关键帧。不要覆盖原项目，完成后保存新项目并报告验证结果。

## 安装与启动

下载对应的 **macOS / Windows ZIP 安装启动包**。包内包含源码与双击脚本，Blender、Python 需另行安装；不是自包含 EXE/DMG。Windows 用户先读 [Windows 安装说明](docs/windows.md)，双击 **Install DKYJ Director.cmd** 安装，再双击 **Launch DKYJ Director.cmd** 启动。下方命令为 Mac 写法，Windows 对应 Python 路径为 `.venv\Scripts\python.exe`。

使用方式：**Mac 电脑使用 Safari，Windows 11 x64 电脑使用 Edge；手机端仅支持 iPhone Safari**，Mac 启动器默认打开 Safari。本机后端验证环境为 **macOS / Apple Silicon、Blender 5.2.1 LTS**；请安装 **Python 3.11+**。测试覆盖及待复测项见 [发布前检查](docs/release-check.md)。Windows 已适配安装启动、局域网 IP、中文字体与路径编码，真实 Windows 显卡与手机链路仍待验收；Linux 不在本次支持范围。从 [Blender 官网](https://www.blender.org/download/) 下载 Mac 版本（M 系列选 Apple Silicon，安装到 Applications），再从 [Python 官网](https://www.python.org/downloads/macos/) 安装 Python 3.11+。

下载源码并解压，在源码目录运行：

```sh
python3 scripts/setup.py
.venv/bin/python scripts/launch.py
```

也可双击 **打开大开眼界导演台.command**。首次安装建立虚拟环境、安装依赖、生成两个演示场景，并安装 Blender 插件。目录移动后重新执行 setup。自定义 Blender 路径可传 `python3 scripts/setup.py --blender /path/to/blender`，启动时设置 `DKYJ_BLENDER`。

保持 Blender 窗口和 3D 视图打开。启动器会使用 Apple Safari 打开电脑导演台；手机与电脑连接同一 Wi-Fi，用 Safari 打开终端打印的手机链接。二维码和最新连接信息位于 `runtime/`。触控可先使用 HTTP，体感需要按下文安装本地证书。

核心功能不需要付费手机 App，也不依赖 Blender MCP。需要 AI 修改模型时，可另外安装 [Blender MCP](https://github.com/ahujasid/blender-mcp)，连接支持该工具的助手；本仓库不捆绑该插件或模型服务。

## 场景项目：模型只建一次

点击页首的项目名称，打开项目库：

1. **保存当前项目**：写入当前模型、人物动画、摄影机与分区。
2. **打开项目**：先自动保存当前场景，再载入目标工程；不重新生成模型。切换后取景暂停，点击「继续取景」恢复。
3. **另存为新项目**：填写名称和场景描述，选择当前场景或已有项目作为模型来源，创建独立副本。后续改模型和关键帧不会修改原项目。
4. **编辑描述**：更新项目简报。描述用于你与 AI 沟通，不会自行调用模型或改变场景。

项目保存于 `projects/library/<id>/scene.blend`，最近一次替换前的副本为 `scene.previous.blend`。目录索引为 `projects/index.json`。重启恢复上次保存的活动项目。关闭 Blender 前请点击网页「保存当前项目」；普通 Ctrl-S 不代替项目库保存。

在对话中告诉助手「切回蒸汽船，沿用模型，再做一个夜间方案」即可让助手通过本地接口选择、复制与修改。命令行和 API 见 [项目接口](docs/project-api.md)。录制或导出时暂不允许切换项目。当前设计为单人、同一控制机位，打开大量项目会增加 Blender 内存占用。

## iPhone 体感转向

Safari 的体感权限需要 HTTPS。此版本为局域网生成项目专用证书，不自动修改任何设备的信任设置。

1. 在 HTTP 页面点击“启用体感”，下载“本地证书”。也可以使用 `runtime/connection.json` 的 `certificate_profile` 链接。
2. 在 iPhone“设置 → 通用 → VPN 与设备管理”中安装 **Blender Local Camera** 描述文件。
3. 到“设置 → 通用 → 关于本机 → 证书信任设置”，手动信任该证书。
4. 返回网页，点击“已信任，打开 HTTPS”。在 HTTPS 页面点击“启用体感”，允许动作与方向权限。
5. 手机按自然持机角度停稳，点击“校准”，再转动手机取景。改变屏幕方向后会重新校准。

该描述文件仅包含本项目的 CA 证书，没有 VPN、代理或设备管理配置。手机安装、信任和权限操作需要本人完成。证书仅适合这台电脑的本地工作流。

每次启动新服务时，启动器会为当前局域网 IP 续签服务器证书（有效期 30 天），沿用原来的项目 CA。CA 有效期一年；更换 CA 后需要在手机重新安装和信任。不要删除 `runtime/tls` 中的私钥；它们已被版本控制忽略。

## 建模、人物动作与录镜头

当前网页是取景控制面板。AI 建模和编排动作在 **Codex 对话中描述，通过 Blender MCP 执行**，网页内暂未接入提示词生成入口或模型服务。

当前演示场景 `examples/steamship_scene.blend` 是 10 秒 / 24 fps 的蒸汽小船：角色从船舱跑上甲板，减速抬头，固定翼飞机从上方掠过。舱内有卧铺、柜台与打开的舱门，甲板有栏杆、木箱、烟囱、系缆桩和长凳。`Camera_Demo` 是预设的跟拍与仰拍示范；`Camera_Phone` 是独立手机机位。人物、飞机、螺旋桨、头部姿态和示范运镜全部保留为 Blender 关键帧，可在时间轴、Dope Sheet、Graph Editor 修改。旧室内场景仍保存在 `examples/calibration_scene.blend`。

1. 选择 `Camera_Phone`，定位时间轴起点，调整机位、焦距、移动速度。
2. “播放”可先检查人物动作节奏。
3. 点击“开始录制”按钮，自动复制一个 `Camera_Take_*` 摄影机并同步播放人物动作。手机移动与转向写入摄影机位置、四元数旋转和焦距关键帧；原有摄影机与人物动作保留。
4. 点击“停止录制”。到时间轴结尾也会自动停止。手机体感与触控随即暂停；点击“继续取景”才恢复。录制后的摄影机仍被选中，便于拖动时间轴回放、手工调整关键帧。
5. 确认页面显示“已录制 X 秒”，再点击“导出 MP4”，后台使用已录好的摄影机轨迹按时间轴渲染 **1280×720 H.264、无音频** 的白模视频。示例使用 24 fps；其他工程沿用自身帧率。完成后网页出现下载链接。

`takes/` 同时保留 `.mp4`、可继续编辑的 `.blend` 快照和渲染日志。文件里没有网页按钮或取景 HUD。点击“继续取景”后会复制到 `Camera_Live`，保留原有录制曲线。即使当前切到 Live 机位，导出仍使用已录制的镜头。没有录好的镜头时禁止导出；“排练”只播放人物动作，不记录运镜。

## 空间总览与 AI 参考导出

电脑端默认打开空间总览，左侧列出空间颜色、名称、近似尺寸和真实镜头小窗；手机仍以取景操控为主，点击“空间总览”进入观察页面。

同一个物理空间只用一种颜色。当前船舱约 4.2 × 4.8 × 2.76 m，前甲板约 5.6 × 7 m / 露天。总览剖开舱顶与部分舱壁，金色摄影机带有方向箭头、完整视锥和路径线。观察机位随真实机位轻微移动，回放、跳帧和导出采用一致的位置关系。

“编辑空间”可增删或修改最多 8 个空间。坐标和尺寸在网页中以米显示，自动换算 Blender 的单位比例；露天空间不显示室内净高。标注已有模型时尺寸用于说明；新空间显示为矩形区域，不自动生成墙壁或陈设。保存后写入 `.blend` 的 `scene['previs_zones']`。

录制完成后点击“导出参考套件”，按同一镜头、帧范围和帧率生成七个文件：

- 纯镜头 MP4：1280×720 H.264，无辅助线、摄影机模型、文字或网页界面。
- 纯俯视 MP4：1280×720，16:9，同步人物、飞机与机位。
- 空间说明 MP4：1920×1080，16:9，包含文字、尺度与俯视画面。
- 空间＋镜头 MP4：1920×2160，上方空间说明，下方真实镜头，便于检查同步关系。
- 空间数据 JSON：空间、单位、动作段落、角色映射、带时间和焦距的机位采样。
- AI 参考说明 TXT：按本段录制范围换算的动作时间、颜色对应关系和素材用法。
- 空间说明图 PNG：尺寸、文字说明与俯视全景。

「简化人物」默认开启，只在导出纯镜头时隐藏本示例的四肢，保留人物色块、位移、朝向、头部姿态；预览和原始关键帧保持完整。取消勾选可导出带四肢的版本。其他项目需给对象设置 `previs_ai_hide` / `previs_ai_show` 后才会启用该简化方式。

优先让纯镜头负责最终运镜和动态；总览或说明图只表达空间关系，避免把观察机位和辅助线带入成片。已核对 [Seedance 2.5 官方白模章节](https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e#LBsudhf9ZoRjNQx8UN0cX3pBn3P)，依据和实现选择见 `docs/seedance-2.5-reference.md`。这些辅助文件不代表平台要求的上传格式。

示例模型由安装脚本首次生成；后续切换直接读取保存文件。源码包包含生成配方，不包含私人工程或渲染视频。


## 验证和开发

```sh
python3 -m compileall -q addon scripts tests
node scripts/test_web_controls.cjs
blender --background --factory-startup --python-exit-code 1 --python tests/test_projects.py
blender --background --factory-startup --python-exit-code 1 --python scripts/test_recorded_export.py
```

当前场景预览约 6–7 fps，最终导出沿用项目帧率；这不是实时 30 fps 视频传输。项目独立性、磁盘恢复、镜头关键帧与导出绑定已验证。真机体感手感取决于手机与网络，尚未建立跨设备验证矩阵。未执行 Seedance 付费生成验证。

## 开源与目录

源码采用 **GPL-3.0-or-later**，完整条款见 [LICENSE](LICENSE)。Blender、Python 及可选 MCP 插件分别遵循其自身许可，不包含在发行包中。本仓库的程序化示例配方随源码发布。

- `addon/`：网页服务、项目库、空间总览。
- `web/`：无框架的本地网页，不依赖 CDN。
- `scripts/`：安装、启动、示例生成、渲染、命令行和打包。
- `tests/`：Blender 项目持久化回归测试。
- [CHANGELOG](CHANGELOG.md)、[开发记录](docs/development-log.md)、[架构说明](docs/architecture.md)。

运行 `python3 scripts/package_release.py` 生成可上传 GitHub 的源码目录和 ZIP。打包采用文件清单，只收录源码、文档与公开示意图；不收录 `projects/`、`runtime/`、`takes/`、`qa/`、虚拟环境和第三方插件。共享作品时请自行挑选导出文件；服务定位为个人局域网工具，不应直接暴露公网。

## 合作联系

项目合作与交流：

- 抖音：**王夹克**
- 微信公众号：**大开眼界AI**
- 邮箱：[826701673@qq.com](mailto:826701673@qq.com)

电脑与手机欢迎页直接显示以上信息；预演台顶部「联系」也可随时展开查看。

发布到 GitHub 的步骤见 [发布说明](docs/github-publishing.md)。

### 分开导出

「镜头 16:9」只导出摄影机画面；「空间 16:9」单独导出空间说明与纯俯视视频；「参考套件」包含全部文件。上下组合视频的每一半都是 1920×1080，总尺寸 1920×2160。见 [导出规格](docs/export-formats.md)。

从 GitHub 网页下载源码后，如 `.command` 启动器提示权限不足，在目录中运行 `chmod +x *.command`，或使用上面的 Python 启动命令。平台 ZIP 已设置启动器执行权限。
