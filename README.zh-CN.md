# 大开眼界导演台 · DKYJ Director

<img src=".github/assets/dkyj-director-hand-eye.png" width="180" alt="大开眼界手与眼睛 Logo">

[English](README.md) · 简体中文

**0.8.0-preview.3 公开预览版**。原来的仓库名字和链接不变，现在首页作为软件下载、说明与更新记录入口。完整应用源码随安装包提供。

## 下载

| 电脑 | 安装包 | 校验 | 电脑浏览器 |
| --- | --- | --- | --- |
| macOS | [下载 Mac 版](https://raw.githubusercontent.com/wangjiake666/dkyj-director/main/downloads/dkyj-director-0.8.0-preview.3-macos.zip) | [SHA-256](https://raw.githubusercontent.com/wangjiake666/dkyj-director/main/downloads/dkyj-director-0.8.0-preview.3-macos.sha256) | Safari |
| Windows 11 x64 | [下载 Windows 版](https://raw.githubusercontent.com/wangjiake666/dkyj-director/main/downloads/dkyj-director-0.8.0-preview.3-windows.zip) | [SHA-256](https://raw.githubusercontent.com/wangjiake666/dkyj-director/main/downloads/dkyj-director-0.8.0-preview.3-windows.sha256) | Edge |

**手机仅支持 iPhone Safari。请下载上表安装包，Code → Download ZIP 包含说明与 downloads/ 下的安装 ZIP，仍需解压其中对应系统的 ZIP。** 软件在自己电脑的 Blender 中运行，不是打开 GitHub 就能使用的云端软件。包内提供源码与启动器，需要另装 [Blender](https://www.blender.org/download/) 和 [Python 3.11+](https://www.python.org/downloads/)，不是独立 EXE/DMG。

[完整安装与使用说明](INSTALL.zh-CN.md) · [这版更新内容](docs/release-notes.md) · [开发日志](docs/development-log.md)

## 开始使用

1. 完整解压。Mac 双击 **Launch DKYJ Director.command**；Windows 先双击 **Install DKYJ Director.cmd**，再打开 **Launch DKYJ Director.cmd**。
2. 欢迎页选择室内排练／蒸汽小船，或描述想要的空间、人数、动作节奏和运镜。AI 制作需按[引导连接 Blender MCP 与 DKYJ MCP](docs/agent-setup.md)，再让自己的 Agent 执行任务；网页不会自行调用模型。
3. 电脑端点击 **连接 iPhone · 扫码运镜**，手机与电脑连同一 Wi-Fi，在 Safari 打开配对链接。体感转向另需按说明配置 HTTPS 证书和动作权限。
4. 用触控、体感、键盘或手柄预览；录制摄影机后导出。镜头和俯视分别为 16:9，可单独导出；合并视频上下各一块 16:9。

## Lite 与 Pro

两种版本共用一个安装包，授权后无需重装。Lite 每项目保存 **3 个场次**，额外场次可临时编辑，手动删旧腾位后保存。触控、体感、键盘录制免费；Xbox / PS5 手柄预览、升降、俯仰和变焦免费。正式项目中的手柄录制由 Pro 解锁，Lite 可进入独立官方场景试录。Lite 导出带 Preview 水印，Pro 无水印并解除场次数量限制。

**爱发电正式商品与自动付款发码尚未接通。** 这次先发布软件预览版；请勿将普通赞助当作 Pro 购买。已有作者签发的有效 v1 码，可在电脑端离线激活。[权益与激活说明](docs/licensing.md)

## 案例、升级与验证

![蒸汽小船空间视图](.github/assets/steamship-board.png)

[室内排练／蒸汽小船示例视频](samples/README.md) · [Xbox / PS5 映射](docs/gamepad.md) · [导出尺寸](docs/export-formats.md) · [Seedance 官方引用](docs/seedance-2.5-reference.md)

升级前保存工程、关闭 Blender 并备份旧目录。解压新版，将原 `projects/` 和 `takes/` 复制到新版，重新安装；不要复制旧 `.venv/` 和 `runtime/`。用新版启动器启动并重新扫码，授权文件仍在系统用户目录。

本轮授权／场次／导出检查和 45 项手柄合成输入检查通过。Windows GPU、iPhone 与 PS5 真机验收仍待完善；详见[检查记录](docs/release-check.md)。安装包包含完整对应应用源码、依赖说明、GPL 许可证与 SHA-256 清单。原有公开历史与版本保留。[源码取得](docs/source-availability.md)

## 联系与合作

抖音：**王夹克** · 微信公众号：**大开眼界AI** · 邮箱：[826701673@qq.com](mailto:826701673@qq.com)
