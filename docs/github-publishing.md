# Publishing on GitHub / 发布说明

Suggested repository name: **dkyj-director**. Display name: **DKYJ Director**. Chinese name: **大开眼界导演台**.

Repository description:

> Local Blender camera previs with a phone viewfinder, editable blocking, reusable scenes, and optional MCP agent integration.

README.md is the default English landing page; README.zh-CN.md is the Chinese manual. Both include the collaboration contact 826701673@qq.com.

**Release target: public preview 0.7.0-preview.2. Publish only the clean allowlisted source directory and platform bundles.**

## Upload the source

1. Run `python3 scripts/package_release.py --platform all` in the working project.
2. Create a GitHub repository named `dkyj-director` in your account.
3. Upload the **contents** of `dist/dkyj-director-0.7.0-preview.2/` to the repository root, including `.github/` and `.gitignore`. Do not upload your working directory or just a ZIP as the only source file.
4. Keep README.md and LICENSE at the root. You can additionally attach the source ZIP and SHA-256 file to a GitHub Release.
5. Check the rendered README, image and Chinese-language link. Repository CI performs source checks; it does not prove local Blender rendering or phone operation.

GitHub's website upload or GitHub Desktop can upload the prepared folder. For a terminal workflow, initialize git **inside the clean release folder**, commit its contents, add the repository URL provided by GitHub, and push. Authenticate with your own GitHub client; do not place credentials in commands or docs.

## About GitHub Pages

No working director backend is deployed through GitHub Pages. Pages supports static site hosting; the renderer needs local Blender/Python/GPU access. The GitHub repository README is enough for download and usage instructions. An optional Pages presentation would be a separate static showcase; none is claimed as deployed in this release.

## 中文

从干净的发行目录上传源码到仓库根目录，GitHub 会直接展示英文 README，点击「简体中文」进入中文版。上传源码不等于部署完整软件；使用者需要下载后在本机安装运行。不要将私人场景、配对 token、证书或录制日志上传。

参考：[GitHub Pages 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)。

发布前核对结果见 [检查记录](release-check.md)。上传当前 0.7 preview.2 干净目录；其中已包含新版手与眼睛 Logo、Safari 安装说明和官方引用。

## 两个平台包

源码仓库仍只有一个：上传无平台后缀的干净 source_directory 内容。GitHub Release 可附两个 ZIP：`dkyj-director-0.7.0-preview.2-macos.zip` 和 `dkyj-director-0.7.0-preview.2-windows.zip`，以及各自 SHA-256。两个包只包含对应系统的双击入口，共享其余核心源码。不是包含 Blender 的离线安装器。
