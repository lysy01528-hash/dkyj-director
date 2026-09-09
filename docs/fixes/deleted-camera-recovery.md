# 删除相机与场景后的恢复 · 0.7.0-preview.5

## 已复现的问题

1. 网页保持连接，在 Blender 删除全部 `Camera_Take_*` 后，`take_name` 仍指向已删除镜头；当前相机可能为空，再次录制无法继续。
2. 录制期间删除相机，旧代码按 `scene.camera` 打关键帧，可能误写另一台机位。
3. 删除空间总览的 Scene 后，`OverviewRig.close()` 再访问 `scene.world`，重现 `ReferenceError: StructRNA of type Scene has been removed`；异常清理后仍保存旧 rig。
4. 外部删除并重建同名 Scene 时，只比较对象名称无法发现数据已替换。项目库缓存也会直接访问已删除 Scene 的 `.name`。
5. timer 捕获异常后再次调用同一个会失败的状态刷新，导致异常逃逸、实时刷新停止。损坏的场景 JSON 也能触发这个路径。

这些症状已在独立测试场景重现；本次没有复现 Blender 进程直接退出，不能把所有原生崩溃归因于这一个原因。

## 修复后的行为

- 每次处理事件前检查 Scene 和相机是否仍属于当前 Blender 数据库与当前场景。删除当前相机后回到可用的 `Camera_Phone`；全部相机删除时重建手机机位。
- 录制绑定创建时的对象身份及相机数据身份。对象被删或移出当前场景会停止该次录制，不向其他相机追加关键帧。已存在的其他 Take 保持独立。
- 清除已删除 Take 的状态、清理无效缓存；总览按 Scene/Object 身份检查并重新搭建，而不只比较名称。
- 总览清理可重复调用，已删除的 helper Scene/Object/Collection/World 不会再次被访问；不删除源场景的用户对象。
- Undo、Redo、打开文件前释放总览与 GPU 资源。新场景就绪后重新绑定；重新发送取景和录制指令即可继续。
- 状态刷新失败时返回可恢复状态，timer 保留。损坏的故事/角色 JSON 显示空列表，不改写原始场景属性。

## 验证记录

2026-09-09，macOS，Blender 5.2.1 LTS。测试均使用独立临时场景，没有删除用户项目中的内容。

| 检查 | 结果 |
| --- | --- |
| 保持 HTTP 连接、删全部 Take、恢复机位与续录 | 通过 |
| 录制期间删当前相机，其他相机无新增关键帧 | 通过 |
| 全部相机删除后重建手机机位 | 通过 |
| 已删除导出目标被拒绝 | 通过 |
| 删除总览 Scene 并重新创建 | 通过 |
| 同名重建 Scene、失效 RNA 重新绑定 | 通过 |
| 损坏 JSON 不终止 timer | 通过 |
| 七种 helper/source 删除与重复关闭 | 通过 |
| 删除项目缓存 Scene 后从磁盘重新加载 | 通过 |
| 原生视窗/GPU/HTTP 与实际 Undo 后恢复 | 通过 |
| 原录制运动、导出归属与保存重开 | 通过 |

后台回归：

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/test_deleted_data.py
blender --background --factory-startup --python-exit-code 1 --python tests/test_overview_lifecycle.py
blender --background --factory-startup --python-exit-code 1 --python tests/test_projects.py
blender --background --factory-startup --python-exit-code 1 --python scripts/test_recorded_export.py
```

GPU 验证使用单独的 Blender 窗口（需要图形桌面，不加 `--background`）：

```sh
blender --factory-startup --python scripts/test_live_deletion.py
```

原生测试结果写入 `qa/live-deletion/result.json`，应为 `ok: true`；测试结束自动关闭测试窗口。GitHub 三系统 Source checks 仅运行不依赖 Blender 的检查，不等于 Windows GPU 或 iPhone 真机验证。本次未新增 Windows 原生 GPU 验证。

## 升级

先保存当前 Blender 项目并退出 Blender。将新版解压后的源码文件覆盖到原导演台目录，保留 `projects/`、`takes/` 和 `runtime/`。Mac 运行 `python3 scripts/setup.py`，Windows 双击 `Install DKYJ Director.cmd`，然后重新启动导演台并刷新电脑/手机网页。仅刷新网页不能替换 Blender 内已经加载的旧插件。
