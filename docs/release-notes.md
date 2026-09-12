# 0.8.0-preview.3 · Lite / Pro public preview

[Download macOS / Windows](https://github.com/wangjiake666/dkyj-director/releases/tag/v0.8.0-preview.3) · [中文说明](../README.zh-CN.md) · [版本权益](licensing.md)

原来的 GitHub 名字与链接保持不变。安装包同时提供 Lite / Pro，升级无需另装专业版；包内附对应 GPL 应用源码。公开案例仍为室内排练与蒸汽小船。

- Lite 每项目保存三个场次，超出可临时编辑，手动删旧后保存。
- Xbox / PS5 手柄预览、升降、俯仰和变焦；Pro 解锁正式项目手柄录制。
- 手机触控／体感和键盘录制可免费使用；Lite 导出带 Preview 水印，Pro 无水印。
- 镜头和纯俯视各 16:9，空间说明板 16:9，可分开导出或上下拼版。
- 保留删除 Take / Scene 后恢复、手机扫码与默认 Camera_Phone。

桌面：macOS Safari / Windows 11 Edge；手机：iPhone Safari。需要另装 Blender 和 Python。这是带源码启动器包，不是独立 EXE/DMG。PS5、iPhone、Windows GPU 实机验收仍待完善；爱发电自动付款发码尚未接通。

升级：保存并关闭 Blender，备份旧目录，完整解压新版，将原 `projects/` 和 `takes/` 复制到新版后重新安装；不要复制 `.venv/` 或 `runtime/`。使用新版启动器并重新扫码。

[检查记录](release-check.md) · [开发日志](development-log.md) · [源码取得](source-availability.md)

联系：抖音 **王夹克** · 微信公众号 **大开眼界AI** · **826701673@qq.com**。

---

# 0.8.0-preview.2 · Local Lite / Pro preview

See [Lite / Pro usage](licensing.md) and [development log](development-log.md). This build adds three saved scenes per Lite project, temporary overflow scenes, offline activation infrastructure, Pro gamepad recording and Preview export watermarks. The platform installers share the same source; Pro does not require a second install.

The production v1 public key is configured; valid author-issued codes can activate Pro offline. The Afdian Pro product and real payment/delivery acceptance remain pending. This local build is not a public commercial launch. Existing 0.7 packages are preserved.

---

# DKYJ Director 0.7.0-preview.5

修复 Blender 中删除 Camera_Take_* / Scene 后无法继续录制、失效 RNA 引用、总览清理失败及实时刷新中断的问题。

- 删除当前相机后恢复 Camera_Phone；录制对象被删除时停止录制，不误写其他机位。
- 清理已删除的 Take / 项目缓存；重建无效总览；Undo / Redo / 打开文件时释放旧绘制资源。
- 保留中性灰界面、绿色下载按钮、手机扫码入口与 HTTP / HTTPS 配对。
- macOS 与 Windows 源码安装包附室内、蒸汽小船案例，不含私人项目与录制。

[复现、修复及验证记录](fixes/deleted-camera-recovery.md) · [完整检查记录](release-check.md)

Mac Blender 5.2.1 上的后台回归和真实 GPU / HTTP / Undo 恢复检查已通过。Windows 原生 GPU 与 iPhone 真机流程未在本次新增验证。

请保存项目、关闭 Blender 后升级并重新运行安装脚本；保留原 projects、takes 和 runtime 文件夹，再重启导演台。

Desktop: macOS Safari / Windows Edge. Phone: iPhone Safari. Blender runs locally; GitHub Pages cannot host the rendering backend.

联系：抖音 **王夹克** · 微信公众号 **大开眼界AI** · **826701673@qq.com**。
