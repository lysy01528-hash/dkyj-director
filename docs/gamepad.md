# 手柄运镜：Xbox / PS5（0.8 预览版）

当前源码已接入 Xbox Series X|S 和 PS5 DualSense 手柄运镜。本页记录当前行为、使用方法和验证边界；它不表示功能已经发布，或已经在所有平台完成真机验收。

## 控制方式

在网页取景台选择「Xbox」或「PS5」类型，再点击「手柄运镜」启用手柄输入。初始类型为 Xbox，选择会保存在当前浏览器；无效保存值回退到 Xbox。按钮会显示等待连接、准备或开启状态。启用后，同一网页内同一时刻只由一种输入控制机位；手机体感切换为停用状态，避免相对摇杆转向和绝对体感姿态同时修改摄影机。键盘、拖动或屏幕按钮接管时，手柄输入暂停。同一时刻请只在一台设备启用控制；当前没有跨手机与电脑的后端控制锁。

| 手柄输入 | 当前行为 |
| --- | --- |
| 左摇杆左右 | 沿当前机位的横向平移 |
| 左摇杆上下 | 沿当前机位的前后移动 |
| 右摇杆左右 | 相对转向 |
| 右摇杆上下 | 相对俯仰 |
| Xbox LT / RT；PS5 L2 / R2 | 下降 / 上升 |
| Xbox LB / RB；PS5 L1 / R1 | 减小 / 增大焦距 |
| 屏幕「升高」/「降低」 | 上升 / 下降 |
| 屏幕「抬头」/「低头」 | 俯仰 |
| 网页「开始录制」按钮 | 使用现有网页按钮开始录制 |

平移以当前机位的方向为参照，因此左摇杆的前后和左右会跟随镜头朝向变化，而不是固定对应世界坐标轴。摇杆会使用死区，松手后输入回到零。界面显示的「机位 Z」是摄影机的世界坐标 Z 值，不是离地高度。A、B 不属于本版控制，也不替代网页录制按钮。

Xbox 使用 LT/RT 升降、LB/RB 调整焦距；PS5 使用标准映射中的 L2/R2 升降、L1/R1 调整焦距。两种类型都只接受 `mapping: "standard"`，不猜测原始 PS5 HID 映射。PS5 的帮助提示会标明使用标准映射，尚未真机验证；PS5 正面按键、触摸板和震动不增加动作。

## 使用步骤

1. 在正在操作导演台网页的那台设备上连接 Xbox Series X|S 手柄或 PS5 DualSense。电脑直接连接手柄；如果用手机操作，则将手柄连接到手机的蓝牙。
2. 手机与运行导演台的电脑连接同一 Wi-Fi，通过软件提供的扫码入口打开 iPhone Safari 取景页。
3. 在取景台点击「手柄运镜」启用手柄；按钮会显示等待、准备或开启状态。
4. 先松开摇杆和扳机，使手柄回到中位，再用左摇杆平移/前后移动、右摇杆转向/俯仰，用 Xbox LT/RT（PS5 L2/R2）升降，用 Xbox LB/RB（PS5 L1/R1）调整焦距。需要时也可使用屏幕上的「升高」「降低」「抬头」「低头」按钮。
5. 需要保存镜头时，仍点击网页现有的「开始录制」和「停止录制」按钮；手柄不负责触发录制。

## 失焦、断连与重连

网页失去焦点、切到后台或手柄断开时，连续输入应暂停并回零，避免页面恢复后继续发送旧的运镜指令。重新连接后，先把摇杆、扳机和肩键全部松开并回到中位，再在网页重新点击「手柄运镜」启用。键盘、拖动和屏幕按钮接管后，回到手柄需要重新点击启用。网络中断时不应积压旧的转向或平移指令。

## 当前验证边界

- Mac Safari 18.6 已真实读到 `Xbox Wireless Controller Extended Gamepad`，`mapping: standard`，四个摇杆轴，以及 LT/RT/LB/RB 对应的输入；双摇杆的示意平移、转向和俯仰也已观察到。
- 生产合成测试已覆盖 Xbox 默认、无效值回退、浏览器记忆、PS5 双摇杆与 L2/R2/L1/R1 标准映射、切换时归零和重新回中，以及非 `standard` 手柄拒绝。没有 PS5 实体手柄，因此 PS5 尚未真机验证。
- 本轮没有读到 A、B，因此没有把它们写入控制方案；这不能证明手柄硬件不支持 A、B。
- Windows Edge 和 iPhone Safari 尚未进行真机输入验收。手机用户本版暂不要求测试。
- 生产 `web/gamepad.js` 与 `app.js` 的 45 项行为测试通过，最大并发控制请求为 1；其中保留原有 Xbox 控制回归。
- 使用生产映射生成的合成手柄输入已在 Blender 5.2.1 LTS 录成 41 帧 Take（1.708 秒）；升降、位置、俯仰和焦距回放一致，并生成了 1280×720 MP4。录制时已修复时间轴 `frame_set` 用旧焦距关键帧覆盖实时变焦的问题，实时变焦现在可进入 Take。导出视频已解码核对为 1280×720、24 fps、41 帧，并检查了首尾画面。
- 上一轮正式 Safari 页面曾用原生界面查看旧版 Xbox 手柄按钮、等待连接引导、四个屏幕控制按钮和机位 Z；本轮新增的 Xbox / PS5 选择器尚未进行原生 Safari 界面复核。当前版本尚未用实体手柄完成这版实际 Blender 录制；上一轮 Mac Safari 18.6 实体探针已读到双摇杆及 LT/RT/LB/RB。

## 参考资料

本页的已测事实来自本项目的生产行为测试、Blender 合成输入录制以及上一轮 Mac Safari 实体探针；探针和原始 JSON 位于不随公开发布包分发的 QA 目录。跨平台能力可参考 [Apple 的 Xbox 手柄说明](https://support.apple.com/en-us/111101)、[PlayStation 的 DualSense 蓝牙连接说明](https://www.playstation.com/en-us/support/hardware/pair-dualsense-controller-bluetooth/)、[Microsoft Edge 的浏览器手柄说明](https://www.microsoft.com/en-us/edge/learning-center/how-to-use-a-game-controller-with-browser-based-games)、[WebKit 的 Gamepad API 介绍](https://webkit.org/blog/7477/new-web-features-in-safari-10-1/)、[W3C Gamepad 规范](https://www.w3.org/TR/gamepad/) 和 [MDN 维护的兼容资料](https://github.com/mdn/browser-compat-data/blob/main/api/Navigator.json)。这些资料不替代本项目的 Windows、iPhone 或实体手柄端到端验收。
