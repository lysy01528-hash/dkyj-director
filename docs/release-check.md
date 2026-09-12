# Release check / 发布前检查

## 0.8.0-preview.3 · 2026-09-12 发布检查

本次发布保留原仓库名字和 URL，公开首页改为安装包、使用说明与公开案例入口。应用逻辑沿用已验收的 preview.2 开发内容，本轮修改集中于发行说明、版本号与公开目录。

- 本轮重新通过 15 项授权、导出策略／水印、项目场次与 Agent 场次测试。
- 网页录制与停止行为检查通过；45 项 Xbox / PS5 生产脚本合成输入检查通过，最大并发控制请求为 1。
- 两平台安装包使用同一生产 v1 公钥，按白名单构建；发布前校验 ZIP CRC、逐文件 SHA-256、私钥／正式授权码／配对 Token 排除、文档相对链接和仅包含两个公开案例。
- 历次真实 Blender 导出与 macOS Safari 场次验收见开发日志。此次没有重新执行实体手柄录制、iPhone、Windows GPU 或 PS5 真机测试，不将打包和合成输入检查视为这些设备已通过。
- 爱发电自动售码尚待账号接入与真实订单验收；本次是软件预览发布。

---

日期：2026-09-06。版本：0.7.0-preview.1。状态：本地发布准备包，未上传 GitHub。

| 核心功能 | 检查结果与证据 |
| --- | --- |
| Blender 下载与安装 | README 中英文均提供 Blender/Python 官方下载链接、安装命令；缺少 Blender 时输出官网链接并停止。不会声称已自动安装 Blender。 |
| Blender MCP 引导 | 欢迎页可展开安装步骤和上游链接；文档区分 Blender 插件、Agent 侧 Blender MCP 服务及 DKYJ 任务 MCP。上游安装命令已核对。当前本机实际通过 MCP 读取场景、摄影机、对象数和帧范围。 |
| 场景对话 | 四步询问空间、人物数量、动作节奏与运镜意图；任务保存、幂等提交、追问回复及状态约束测试通过。外部 Agent 需要用户启动一次对话，不会仅因提交简报自动运行模型。此前完整网页→MCP→追问→保存链路记录见开发日志。 |
| 不同项目 | 当前本地诊断发现 5 个项目；独立场景、相机、动画数据及保存重载测试通过。切换复用已存模型，不重新生成。 |
| 16:9 导出 | 已有实际 24 帧样片经解码确认：POV 1280×720，纯俯视 1280×720，空间说明板 1920×1080，拼版 1920×2160。拼版上下各 1920×1080，各自 16:9。 |
| 分开与合并 | 镜头、空间、参考套件三个入口；空间独立模式实际输出 6 帧，不需要 POV 或拼版文件。录制镜头绑定和缺失产物拒绝测试本轮重新通过。 |
| Safari | Mac 启动器显式选择 Apple Safari，iPhone 指南同样使用 Safari，体感 HTTPS/证书/动作权限步骤齐全。本轮电脑锁屏，Safari UI 和真机交互未能重新验证，不能视为全部真机验收通过。 |
| 官方引用 | Seedance 2.5 发布说明本轮可读，白模说明链接和此前核对摘要已保留；飞书手册本轮抓取失败，已注明。未宣称官方认证或拼版为官方上传规范。 |
| Logo | 已替换为手与眼睛的手绘透明 PNG，真实 alpha 检查通过；旧人物头像不进入此发布包。 |
| 打包 | 白名单源码、双语说明、许可证、官方引用、Logo、开发日志、校验清单；私人项目、证书、配对信息、QA、虚拟环境和第三方插件不打包。 |

## 本轮执行

- Python 源码编译检查、网页控制行为测试、创作任务单元测试。
- Blender 后台：tests/test_projects.py、scripts/test_recorded_export.py、tests/test_export_files.py。
- 本地连接诊断及真实 Blender MCP 场景读取；HTTP 检查欢迎页安装引导实际提供。
- 发布包 ZIP CRC、清单 SHA-256 与文档本地链接完整性检查。

## 本人发布前试用

在已解锁的 Mac Safari 打开新版欢迎页，展开安装引导，检查四步问答和项目列表；iPhone Safari 录一段转向与平移，分别下载镜头、空间视频和参考套件，确认运动及下载行为。此项需要真实设备，后台测试不能代替。

English: Core persistence, camera ownership and export checks pass locally. Safari is the documented target and default Mac launch browser. The final interactive Safari/iPhone smoke test remains pending because the Mac was locked during this audit. Publish from the clean release folder only.

preview.4 补充公开联系信息：欢迎页直接展示抖音、微信公众号和邮箱，预演台顶部提供联系菜单，手机布局不隐藏。说明与发布包同步；本次不改动录制和导出逻辑。

## Windows 与双平台包补充

Windows 自动搜索 Blender、虚拟环境路径、中文路径、中文字体选择、不同语言的 ipconfig、离线降级与手动 LAN IP 覆盖的 6 项测试通过（在 Mac 执行分支测试）。Mac 与 Windows 的手机支持均限定 iPhone Safari；Windows 桌面 Edge。新增三系统 CI 配置尚未上传运行；没有将其作为已通过证据。真实 Windows 安装、显卡渲染、防火墙与 iPhone 连接待设备验收。

双平台改动后再次实际渲染 6 帧完整参考套件，并解码确认纯镜头与纯俯视 1280×720、空间板 1920×1080、上下拼版 1920×2160，四路均为 6 帧。隔离目录生成的 HTTPS 证书 SAN 与共享 IP 列表一致；未替换当前会话证书。两个 ZIP 已核对 CRC、逐文件 SHA-256 与平台启动脚本分离。以上实际渲染在 Mac 完成，不能代替 Windows 显卡测试。

## 0.7.0-preview.2 · 公开发行检查

2026-09-06：本次重新通过 Python 编译、四个网页脚本语法检查、网页控制行为测试、2 项创作任务测试和 6 项平台分支测试。独立 Blender 进程重新通过项目场景／网格／动画隔离与磁盘重载、录制摄影机绑定、无录制导出拒绝、空间独立导出及缺失产物拒绝测试。

公开案例使用明确文件清单：室内排练、蒸汽小船的历史 POV / 俯视视频，以及现有场景生成脚本。个人项目库与录制、QA、运行时目录均不进入发布目录。源码与双平台 ZIP 的内容、校验清单和本地文档链接在上传前检查。上述历史 Safari / Windows 真机验收边界仍适用。


## 0.7.0-preview.3 · 2026-09-07

- Native macOS Safari: header pairing button opens the dialog; HTTP QR loads, copy link confirms success, HTTPS switch updates URL and QR. Neutral UI verified visually; scene images retain color.
- Local HTTP and HTTPS QR endpoints returned PNGs; requests without the pairing token returned 403.
- Seven platform tests pass, including proxy benchmark network and broadcast address exclusions. Web controls behavioral checks pass.
- Physical iPhone scanning and Windows GPU rendering are not newly verified by this update.


## 0.7.0-preview.5 · 2026-09-09

删除 Take / Scene 与失效 RNA 修复，通过八项删除回归、七种总览清理场景、项目缓存重新加载、录制导出回归，以及原生视窗中的 GPU/HTTP/Undo 恢复检查。测试在 macOS Blender 5.2.1 上执行。[完整修复记录](fixes/deleted-camera-recovery.md)。
