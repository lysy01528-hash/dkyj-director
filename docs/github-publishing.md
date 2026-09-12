# GitHub distribution / GitHub 发布方式

The public download address stays **https://github.com/wangjiake666/dkyj-director**.
Version **0.8.0-preview.3** replaces the current repository tree with the bilingual
download guide, examples and release documentation. The name and URL stay the same.
No separate download repository or visibility change is needed.

## Download and source

Download the macOS or Windows ZIP from [Releases](https://github.com/wangjiake666/dkyj-director/releases/tag/v0.8.0-preview.3).
Each platform uses one Lite/Pro package and includes the corresponding application
source, dependencies, GPL license and a per-file SHA-256 manifest. **Code → Download ZIP**
only downloads this repository’s documentation, not the runnable application.
See [source availability](source-availability.md).

Development files and seller tools remain local. Signing keys, activation-code
inventory, account credentials and user projects are excluded. Update the public
repository with a normal commit based on its existing main branch; do not merge the
local commercial development branch or rewrite the existing public history.

## Preview status

Offline Pro activation is implemented and the production v1 public key is included.
The Afdian product link and real automatic order delivery are not ready. This release
is a software preview, not a verified launch of automated paid delivery.

## 发布和升级

1. 构建并校验两个平台包、SHA-256、逐文件清单、隐私排除与文档链接。
2. 公开仓库仅同步下载说明、公开案例、许可证和日志，保留原名字与链接。
3. Release 标为预览版，上传 Mac / Windows 共用 Lite-Pro 包及校验文件。
4. 无登录下载两个包并回验哈希，再记录发布地址和结果。

升级前保存工程、关闭 Blender 并备份原目录。新版完整解压到新目录，复制原
`projects/` 和 `takes/` 到新版目录，重新运行安装步骤。不要复制旧 `runtime/`、
证书和 `.venv/`；启动新版后重新扫码。用户授权存于系统用户目录，独立于安装目录。
旧版本发布记录保留；旧链接、公开副本和 GPL 接收者权利不会被撤回。

macOS 包使用 `.command` 和 Safari；Windows 包使用 `.cmd` 和 Edge。
手机仅支持 iPhone Safari。需要另装 Blender 和 Python，并非独立 EXE/DMG。

## GitHub Pages

GitHub Pages can host a static introduction but cannot run the local Blender renderer.
See [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

联系：抖音 **王夹克** · 微信公众号 **大开眼界AI** · **826701673@qq.com**。
