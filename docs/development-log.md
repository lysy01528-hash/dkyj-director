# 开发记录

## 2026-09-06 · v0.7.0-preview.2（公开预览发行）

整理独立的干净源码目录和 macOS / Windows 安装包；公开案例限定为室内排练和蒸汽小船，附历史演示视频、案例说明及本地场景生成脚本。发布白名单不读取个人项目库、录制目录和 QA 目录。保留原有安装、Blender MCP、手机 Safari、双路 16:9 导出、联系信息和官方引用。

本次修改集中于发行内容与说明，不改变应用控制与渲染代码；验收范围和未完成的真机检查见 release-check.md。

## 2026-09-06 · v0.7.0-preview.1（双平台包，未发布）

适配 Windows 路径、安装启动、局域网 IP、证书地址、中文字体和 UTF-8 数据，保留 macOS Safari。Windows 提供两个 CMD 双击入口，电脑打开 Edge，手机仅支持 iPhone Safari。自定义 Blender 路径成功安装后保存在本地。

打包脚本输出一个干净源码目录、macOS 与 Windows 两个 ZIP，各自有入门说明和对应启动脚本。Windows 版属于待真机验收预览：本轮在 Mac 执行跨平台分支测试，配置了 Windows CI，但没有实际运行远端 CI，也没有 Windows GPU／手机运镜验收。

## 2026-09-06 · v0.6.0-preview.4（未发布）

欢迎页与预演台「联系」菜单展示抖音：王夹克、微信公众号：大开眼界AI、邮箱：826701673@qq.com。手机端同样可见；邮箱可点击。同步中英文 README 与发布包，不修改录制、项目或导出功能。

## 2026-09-06 · v0.6.0-preview.3（发布前检查，未发布）

欢迎页新增可展开的首次安装引导，链接 Blender、Python 和 Blender MCP；缺少 Blender 时显示官方下载地址。Mac 启动器显式使用 Safari，双语 README、试用指南同步电脑与 iPhone 的 Safari 流程。Logo 根据反馈删除人物脸部，改为单手与大眼睛，最终采用真实 RGBA PNG。

重新通过任务追问与持久化测试、网页控制测试、Blender 项目独立与重载、录制机位归属、导出文件验证；实际 MCP 场景读取成功。现有实际视频尺寸和独立空间输出证据已核对。官方 Seedance 发布页复核成功，飞书手册本轮抓取失败已记录。Mac 锁屏阻挡 Safari UI 复测，不将此项写为通过。完整范围见 release-check.md。

## 2026-09-06 · v0.6.0-preview.2（未发布）

新增“镜头 16:9”和“空间 16:9”独立导出入口。空间说明板重排为 1920×1080；纯镜头、纯俯视保持 1280×720。组合视频为 1920×2160，上下各 1920×1080，保留画面比例。空间单独导出不依赖镜头文件，下载列表按模式校验完整产物。

另实际渲染 6 帧独立空间模式，确认产出空间视频且无需生成纯镜头或组合视频。本机插件已更新并重启，浏览器显示两个独立导出按钮；未录制时按钮保持禁用。

实际渲染 24 帧套件并用 Blender 视频编辑器解码检查四路视频尺寸，目视检查组合视频上下画面及文字排版。网页控制回归、录制镜头绑定回归和导出文件完整性测试通过。验证范围为本机 Blender 与浏览器，不替代手机真机复测。

使用内置图片生成工具完成黑墨线手绘导演标志：圆眼镜、双手取景框、运镜箭头。确认 PNG 真实透明，已置入中英文 README。详细生成记录见 logo-generation.md。源码打包包含新资产、日志与导出说明；未发布到 GitHub。

## 2026-09-06 · v0.6.0-preview.1（未发布）

新增欢迎页、四步创作简报、手机大开眼界品牌和本地任务队列。可选 DKYJ stdio MCP 提供读取任务、创建或恢复项目、追问、进度回报和保存完成工具；Blender MCP 负责场景编辑。两个接口不包含内置模型或后台 Agent 调度。

验收：真实浏览器提交简报，MCP 协议握手与五个工具列举成功，prepare_brief 创建独立项目，report_brief 提问显示网页，用户补充回传，继续后复用同一项目。通过 Blender MCP 采样 1/120/240 帧确认人物、飞机和示范摄影机位置变化，finish_brief 保存后网页进入可预演。此验收复用已有模型与动画，不宣称测试了任意新场景的自动生成能力。

任务存储、幂等提交、追问持久化、完成前验证字段和制作中回复限制测试通过。项目独立性、磁盘恢复、网页输入节流、录制镜头归属及导出快照回归通过。另从该独立项目实际渲染了 24 帧纯镜头、俯视和组合视频，输出与同步机位采样正常。手机布局检查使用浏览器 393×852 和 852×393 尺寸，不代替 iPhone 真机手感测试。


## 2026-09-06 · v0.5.1

补充英文默认 README、完整中文说明、合作邮箱、Agent 接入和 GitHub 发布步骤。明确 GitHub Pages 仅能托管静态页面，导演台需本机 Blender；MCP 插件与 Agent 服务需分别配置。增加只读连接诊断，区分端口可达与 Agent 工具调用成功。本机诊断通过；通过 MCP execute_blender_code 实际读取 Steamship 场景，确认 Camera_Demo 与 92 个对象可访问。此结果证明当前本机链路，不代表所有 Agent 均已适配。


## 2026-09-06 · v0.5

目标：场景模型复用、不同项目切换、整理公开源码。

设计：ProjectStore 保存独立 Scene 快照；切换先保存当前，再载入目标。项目描述与模型文件分开索引，描述不会自动触发模型重建。网页保留当前清爽空间研究布局，项目库以双栏对话框承载。

已验证：Blender 5.2.1 中复制后的 Scene、摄影机数据和 Action 独立；保存后重新载入保持动画变化、项目简报和活动 id；自动重名后录制机位与角色引用正确；路径穿越和缺失项目文件拒绝；既有网页输入行为及录制导出快照回归通过。桌面浏览器成功创建复用模型的备用方案，并在室内/蒸汽船间切换；冷启动恢复保存项目及实时画面通过。从项目快照实际完成 24 帧纯镜头、总览与组合视频渲染。发行目录中的程序化蒸汽船生成和独立项目回归测试通过。

验证输出保存在本机 qa/，不随开源包发布。回归脚本随源码提供。跨平台适配和跨设备真机体感矩阵尚未完成。

## 先前版本

v0.4 完成蒸汽小船动作、陈设、米制空间说明和三路同步导出。通过实际 MP4 解码检查了模型与摄影机运动；未执行 AI 视频平台生成。

v0.2–0.3 修正录制后机位被实时传感器覆盖及导出使用错误摄影机的问题，引入录制 Take 归属和停止后输入暂停。总览渲染采用先准备场景、后 GPU 绘制的方式，避免在绘制回调中切场景引起锁死。

双平台改动后再次实际渲染 6 帧完整参考套件，并解码确认纯镜头与纯俯视 1280×720、空间板 1920×1080、上下拼版 1920×2160，四路均为 6 帧。隔离目录生成的 HTTPS 证书 SAN 与共享 IP 列表一致；未替换当前会话证书。两个 ZIP 已核对 CRC、逐文件 SHA-256 与平台启动脚本分离。以上实际渲染在 Mac 完成，不能代替 Windows 显卡测试。


### 2026-09-07 · GitHub CI fixture correction

The Windows discovery test clears the environment to isolate Blender installs. It now supplies HOME and USERPROFILE for its temporary user directory, so Path.home() works on native Windows runners. Application code and the preview.2 release bundles are unchanged.


## 0.7.0-preview.3 — 2026-09-07

- Added prominent phone-pairing buttons to the desktop header and welcome page, with local QR codes, copyable links and iPhone Safari setup instructions.
- HTTP and HTTPS QR codes are generated locally and require the active pairing token; no external QR service is used.
- Changed interface colors to neutral grayscale while preserving scene, actor and exported video colors.
- Corrected the isolated Windows CI test user-home environment.
- Excluded proxy benchmark addresses and interface broadcast addresses from phone pairing links.
