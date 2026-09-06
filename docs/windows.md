# Windows 安装 / Windows setup

Windows 版与 macOS 版共用场景、项目、关键帧及导出代码。Windows 目标为 Windows 11 x64；当前完成跨平台代码与分支测试，尚未在真实 Windows GPU / iPhone 链路验收。手机端只支持 **iPhone Safari**，不提供 Android 支持。电脑端 Windows 使用 Edge，macOS 使用 Safari。

## 首次安装

1. 下载 Windows ZIP 并**全部解压**到自己的文件夹（不要在压缩包里运行）。
2. 从 [Blender 官网](https://www.blender.org/download/) 安装 Blender 5.2 系列的 Windows x64 版本；从 [Python 官网](https://www.python.org/downloads/windows/) 安装 Python 3.11+，保留 Python launcher 或勾选 Add Python to PATH。
3. 双击 `Install DKYJ Director.cmd`。它建立 `.venv`、安装依赖、首次生成房间／蒸汽船演示场景并安装导演台插件；不会捆绑或下载 Blender 本体。
4. 双击 `Launch DKYJ Director.cmd`。保持 Blender 窗口及 3D 视图打开；启动器打开电脑 Edge 并打印手机配对链接。缺少初始化文件时会先运行安装。
5. 如果 Windows 防火墙询问，允许 Blender 在当前可信的**专用网络**上通信。手机和电脑连同一 Wi-Fi，iPhone 用 Safari 打开配对链接。体感按中文 README 安装项目证书并手动信任，然后允许 Safari 动作权限。

不需要管理员模式，不调整 PowerShell 执行策略。普通预演不需要 MCP；AI 制作需要 [Agent 接入](agent-setup.md) 中的两个 MCP 服务。

## 常用命令（PowerShell，在解压目录运行）

```powershell
py -3 scripts/setup.py
.\.venv\Scripts\python.exe scripts/launch.py
.\.venv\Scripts\python.exe scripts/doctor.py
.\.venv\Scripts\python.exe -m pip install -r requirements-agent.txt
.\.venv\Scripts\python.exe scripts/agent_config.py
```

把 DKYJ 配置输出加入自己的 Agent，再配置 Blender MCP。若客户端需要 `uvx.exe` 的完整路径，用 `where.exe uvx` 查询。适用通用 JSON 的 Blender MCP 配置在 agent-setup.md；该文档的上游链接有各客户端 Windows 示例。

自定义或便携版 Blender：

```powershell
py -3 scripts/setup.py --blender 'D:\Apps\Blender\blender.exe'
```

成功安装后路径保存在本机 `runtime/setup.json`，以后双击启动会复用。需要临时覆盖可设置 `DKYJ_BLENDER`。复制到另一台电脑时重新解压安装，不复制旧 `.venv`、证书或运行目录。

## 手机连接或导出问题

- 手机打不开：先确认可信专用网络、同一 Wi-Fi、未开启访客隔离；允许 Blender 的 TCP 8765/8766 入站。不要把这些端口映射到公网。
- 多网卡/VPN 选择了错误 IP：用 `ipconfig` 找 Wi-Fi 的 IPv4，在 PowerShell 设置 `$env:DKYJ_LAN_IP='192.168.1.10'`（替换为自己的地址），关闭专用 Blender 窗口后从同一终端启动。服务器链接与 HTTPS 证书共用此地址。
- 找不到中文字体：Windows 一般使用 Microsoft YaHei；安装中文补充字体，或把 `DKYJ_FONT` 指向自己的中文 `.ttf` / `.ttc` 字体。此包不分发系统字体。
- 没有画面：保持 Blender 的可见 3D 视图打开，并检查 [Blender 显卡要求](https://www.blender.org/download/requirements/)。远程桌面/虚拟机的 GPU 行为未验证。

## English

Extract the Windows ZIP, install Blender 5.2 and Python 3.11+, run **Install DKYJ Director.cmd**, then **Launch DKYJ Director.cmd**. Desktop: Edge. Phone: iPhone Safari only, on the same Wi-Fi. Permit Blender on your trusted Windows Private network if prompted. Use `.venv\Scripts\python.exe` instead of `.venv/bin/python` in shared documentation. A custom Blender path passed to setup is saved locally. Windows branch tests pass on the development Mac; native Windows rendering and phone operation remain to be tested.

Apple no longer supplies Safari updates for Windows: [Apple Support](https://support.apple.com/en-ca/102665).
