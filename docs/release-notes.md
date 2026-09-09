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
