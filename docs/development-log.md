# 开发记录

## 2026-09-12 · preview.3 保留原 GitHub 链接发布

作者明确要求先更新现有仓库，名字与链接保持不变。因此公开地址继续使用 `wangjiake666/dkyj-director`，当前目录改为中英文下载说明、公开案例、许可证与日志；开发与卖家工具留在本地，不将商业开发分支整段推送到公开仓库。使用正常提交更新目录，保留历史，不新建下载仓库。

发布为 0.8.0-preview.3 软件预览版，Mac / Windows 各一份 Lite-Pro 共用包，内含完整对应应用源码与逐文件校验清单。沿用已配置的生产 v1 公钥，免费三场次、手柄预览／Pro 录制、水印、手机扫码、独立与拼版 16:9 导出和两个公开案例一起提供。自动购买发码仍待配置及实单验证，说明与购买入口保留未配置状态。

GitHub Release 已公开发布，四个附件通过无凭据官方 API 下载并回验 SHA-256。由于当时 Release 直接下载 URL 返回 404，在原仓库 `downloads/` 提供同字节镜像，首页使用镜像下载入口。发布检查与下载回验记录见 [release-check.md](release-check.md)。此前日志描述的是当时状态，以此条及最新检查记录为准。

## 2026-09-12 · 爱发电卖家 API 补货

作者后续指定采用官方 Webhook/API 文档。读取实际页面 2025 年补货和方案查询更新，新增开发者专用 CLI：官方 MD5 协议签名（授权码仍是 Ed25519）、方案/SKU 核对、默认预览、仅追加库存、SQLite 码哈希防重复、超时停止重发与回读核对、已完成订单的实际发码比对。客户端不存爱发电 Token，不新增联网授权，也不需要 Webhook 服务器。

8 项本地行为测试通过，包括官方签名向量、中文内容、既有库存保留、重复/并发补货与超时核对；与授权、发证测试共 19 项通过。卖家端使用 certifi 验证 HTTPS，ifdian.net 与 afdian.com 实际无凭据探测返回缺参码 400001，不视为账号接通。新增仅监听 loopback 的一次性连接页，便于在 Safari 输入 Token，不在聊天或命令参数传入。未使用真实 API Token 或订单。实际账号连接与订单交付仍待完成；本轮公开包不包含卖家配置。


## 2026-09-12 · 生产 v1 激活码与 preview.2

作者明确确认生成 10 个正式销售码并配置生产公钥。密钥采用 Ed25519，生产私钥加密保存到应用和 Git checkout 外的私有目录，口令写入 macOS 钥匙串并回读核验；源码与安装包只含公钥。每码唯一 ID/nonce，按商业 v1、Pro、无到期时间签发，未导入爱发电或上传 GitHub。

使用软件默认生产公钥逐枚验证 10 个码，分别离线激活并通过 10 次独立进程重启验证；错误码不改原授权文件，其他密钥签发的码被拒。全部使用隔离授权存储，不占用作者本机授权。保留 preview.1，输出新的 preview.2 双平台包；商品购买与自动发码尚待实测。


## 2026-09-12 · Lite / Pro 商业化本地开发

确认范围：Lite 每项目最多保存 3 场，超出为临时编辑，需用户手动删旧场次腾位，不能自动覆盖；只限制手柄录制，非手柄录制可用且免费导出带水印；Pro 去水印；两种权益共用一个安装包。当时拟采用私有开发仓库＋独立公开下载仓库；后续已按下方最新发布决定改为保留原下载链接。安装包保留 GPL 对应源码。

完成离线验签与状态 UI、开发者发证工具、三场次目录／迁移备份／草稿保护、MCP/CLI 场次命令、手柄录制后端检查、独立 Demo、各导出路径水印。修复新增场次缓存读取被删除 Scene 的 RNA 问题；控制器继续使用原有 Xbox/PS5 输入数学与串行发送通道。新增命令从 HTTP 排队到主线程执行再次检查，不将 HTTP 202 当保存完成。

验证：授权／库存测试、真实 Blender 手柄门控、原相机删除恢复、真实多场次保存／删旧／Pro／重启回归；原 45 项 JS 手柄测试及网页控制回归；完整 POV/spatial/overview 三模式六帧导出、1280×720/1920×1080/1920×2160 输出以及 23.976 FPS，Pro 路径哈希一致。独立 GUI 主机通过实际 HTTP 验证删旧释放名额后保存临时场次；Demo 实机进程与正式测试项目隔离，退出采用当前 Blender 支持的执行方式，已实测服务关闭与返回地址保留。

界面已查看 Lite 授权面板、错误码提示、项目与场次计数。旧原生删除确认使内置测试浏览器交互阻塞，改为页面内确认后，在原生 macOS Safari 实际完成：新建第 2/3 场→第 4 场草稿→超限拒绝保存→确认删除旧场→额度降为 2/3→保存草稿恢复 3/3。补充命令发送失败时解除操作等待、Agent 不把上一条旧错误当成本次结果的处理。Windows/iPhone/PS5 实体与完整商业购买链路仍未验收。

销售配置：尚无正式 Pro 商品链接、生产公钥或销售库存，没有付费下单，没有上传或修改远端可见性。没有将测试私钥／注册码、用户项目、私人案例、运行数据和发证工具放入用户安装包。安装包是带源码的启动器包，不是独立 EXE/DMG。


## 2026-09-11 · Xbox / PS5 手柄运镜接入（Unreleased）

当前源码已接入 Xbox Series X|S 和 PS5 DualSense 手柄。手柄按钮旁提供 Xbox / PS5 类型选择，初始为 Xbox 并由当前浏览器记忆；点击「手柄运镜」后，左摇杆负责相对当前机位方向的横移与前后移动，右摇杆负责相对转向与俯仰，Xbox 的 LT/RT 或 PS5 标准映射 L2/R2 负责升降，Xbox 的 LB/RB 或 PS5 标准映射 L1/R1 负责焦距；屏幕提供「升高」「降低」「抬头」「低头」四个按钮，录制继续使用现有网页按钮。A/B、PS5 正面按键、触摸板和震动不纳入本版控制。

手柄模式与手机体感互斥；在同一网页内，键盘、拖动或屏幕按钮接管时暂停手柄输入。同一时刻请只在一台设备启用控制，当前没有跨手机与电脑的后端控制锁。网页失焦、切到后台或手柄断连时暂停连续输入并回零；重连后先回中，再重新点击「手柄运镜」启用，不积压旧的移动或转向指令。界面「机位 Z」显示世界坐标 Z，不是离地高度。

生产 `web/gamepad.js` 与 `app.js` 的 45 项行为测试通过，最大并发控制请求为 1，覆盖 Xbox 默认/无效值回退/浏览器记忆、PS5 标准映射、切换归零与回中、录制中切换、非 `standard` 拒绝和标签更新。使用生产映射生成的合成手柄输入已在 Blender 5.2.1 LTS 录成 41 帧 Take（1.708 秒），升降、位置、俯仰和焦距回放一致，并生成了 1280×720 MP4。时间轴 `frame_set` 覆盖实时变焦的问题已修复，录制时保存并恢复 lens，实时变焦可进入 Take。上一轮正式 Safari 页面曾用原生界面查看旧版 Xbox 手柄按钮、等待连接引导、四个屏幕控制按钮和机位 Z；本轮新增的 Xbox / PS5 选择器尚未进行原生 Safari 界面复核。

当前版本尚未用实体手柄完成这版实际 Blender 录制；上一轮 Mac Safari 18.6 实体探针已读到 Xbox 双摇杆及 LT/RT/LB/RB。PS5 没有实体手柄，Windows Edge 与 iPhone Safari 尚未真机验收；手机使用时，手柄应连接正在操作网页的手机，手机通过同一 Wi-Fi 的扫码入口打开 Safari。A/B 本轮没有读到。实现和复测细节见 [手柄运镜说明](gamepad.md)。

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

## 0.7.0-preview.4 — 2026-09-07

- Phone pairing links open the viewfinder directly and select Camera_Phone once per project; legacy iPhone links also select the phone camera.
- Live control copies use Camera_Phone; animated source cameras and recorded takes remain intact.
- Recorded camera motion and export ownership regression checks pass.

### 2026-09-07 · Download action visibility

Changed the export download link into a solid green button with white text, arrow and keyboard focus outline. The remaining UI stays neutral gray; hidden downloads stay hidden.


## 2026-09-09 · 删除 Take / Scene 后的实时连接恢复

用户报告：网页保持实时连接时在 Blender 删除多条 Camera_Take_*，再次录制失败，并出现 StructRNA of type Scene has been removed。独立场景复现了相同 ReferenceError、网页 timer 错误恢复再次抛异常，以及录制相机删除后仍给其他机位写关键帧的风险。没有据此断言所有用户遇到的进程崩溃都来自同一原因。

修复相机录制归属、Scene/Object 有效性验证、总览资源清理、项目缓存失效、Undo/Redo/文件加载前释放绘制资源，并为异常状态提供不访问旧 RNA 的 JSON 回退。删除当前镜头后保留其他机位与已有录制；缺少相机时恢复 Camera_Phone。

已通过 8 项删除回归、7 种总览清理场景、7 项原生视窗/GPU/HTTP/Undo 检查，项目缓存重新加载与录制导出回归通过。实际测试环境：macOS / Blender 5.2.1 LTS；未验证 Windows 原生 GPU。详见 [修复记录](fixes/deleted-camera-recovery.md)。
