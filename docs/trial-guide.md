# 0.6 试用指南 / Local preview trial

此包供本机试用，尚未发布 GitHub。原有场景和录制文件不会被放进公开源码包。

## 第一次进入

1. 按 README 从官网下载 Blender 与 Python，运行安装脚本。Mac 使用 Safari，Windows 按 windows.md 安装后使用 Edge 启动导演台；欢迎页“第一次使用”可展开 MCP 安装引导。欢迎页回答场景、人物、动作、镜头四个问题，确认并选择复用模型。
2. 提交后应显示「等待 Agent」，不是「生成完成」。没有连接 Agent 时任务仍会保存，可稍后继续。
3. 在自己的 Agent 中配置 DKYJ Director 和 Blender MCP。安装和配置见 agent-setup.md。
4. 发给 Agent：「执行下一个 DKYJ 创作任务，保留关键帧，不覆盖源项目。」
5. Agent 需要你补充时，欢迎页显示问题；回复后让 Agent 继续读取任务。完成后点击「打开项目，开始预演」。

欢迎页右上角可直接进入预演台；之后通过「创作首页」返回。网页草稿仅保存在该浏览器，已提交任务保存在本机 projects/briefs.json。项目和任务均不自动上传。

## 手机与镜头

iPhone 使用 Apple Safari，在同一 Wi-Fi 下打开本机手机链接。检查大开眼界标识、摇杆、拖动转向和升降按钮。体感需 HTTPS、本地证书信任和 Safari 动作权限。选择手机机位，开始录制后再运镜，停止后回放，最后导出。

重点试用：自己的场景描述是否够自然；Agent 生成的动作是否符合节奏；人物数量与颜色是否正确；保存切换后是否保留；手机握持、转向和延迟是否合适。当前预览帧率不等于最终导出帧率。

## 范围

已完成的网页任务流和 MCP 接口不代表所有 Agent 都能自动执行。Agent 需具备本机 MCP 能力，且用户需启动对话执行；模型能力、上下文和工具授权影响结果。本版不内置模型、不安排后台持续唤醒，不宣称一键生成任意场景成功。

English: This is a local trial, not a published release. Submit a brief in the welcome UI, start a turn in your MCP-capable agent, let it use DKYJ tools and Blender MCP, inspect its result, then record on the phone. Unconnected tasks remain waiting. Validate phone handling on your device before publishing the project.

## 导出核对

“镜头 16:9”导出纯镜头；“空间 16:9”导出带说明的空间板与纯俯视；“导出参考套件”另包含上下拼版。空间板 1920×1080，纯镜头与纯俯视 1280×720；拼版 1920×2160，上下各 1920×1080（各自 16:9，整个拼版不是 16:9）。帧范围与帧率保持同步。
