# 项目与场次接口 · v0.7

Windows: replace `.venv/bin/python` with `.venv\Scripts\python.exe`; use `py -3` instead of `python3`. Phone support is iPhone Safari only. See [Windows setup](windows.md).

接口服务由 Blender 插件启动，所有模型读写在 Blender 主线程执行。自然语言的理解由外部助手负责；网页保存描述，不内置文本生成模型。切换只载入存储的场景。一个项目可以包含多个独立场次；空间分区、角色和 Camera Take 不是场次。

## CLI

在仓库根目录、导演台运行时执行：

```sh
.venv/bin/python scripts/projects.py list
.venv/bin/python scripts/projects.py save
.venv/bin/python scripts/projects.py switch --id steamship
.venv/bin/python scripts/projects.py create --name '蒸汽船第二方案' --description '复用船舱和甲板，调整人物出舱节奏' --source current
.venv/bin/python scripts/projects.py update --id PROJECT_ID --name '新名称' --description '新的场景简报'
.venv/bin/python scripts/projects.py scene_create --name '第二场追逐' --description '出弯后红车反超'
.venv/bin/python scripts/projects.py scene_save
.venv/bin/python scripts/projects.py scene_switch --id SCENE_ID
.venv/bin/python scripts/projects.py scene_delete --id SCENE_ID
.venv/bin/python scripts/projects.py scene_discard
```

`list` 返回活动项目及项目 id、名称、描述、更新时间和可用状态。助手先读取列表，匹配用户描述，再使用 id。不得仅因名称相似覆盖已有项目。`create` 的 source 可为 current 或列表里的 id，创建后自动切入；随后通过 Blender MCP 或 Blender 编辑当前场景，再执行 save。

`scene_create` 默认创建一个可保存场次；免费版每个项目最多保存 3 个场次。超过 3 个后仍可继续创建临时草稿，但 `scene_save` 会拒绝，直到用户手动删除一个旧场次。系统不会自动删除或覆盖旧场次。离开草稿前必须使用 `scene_discard`，或者在 `scene_switch` / `scene_create` 中明确传 `--discard-draft`。CLI 输出的 `scenes.draft` 是临时状态，不能当作已保存场次。

Pro 与 Lite 使用同一安装包。是否允许 Pro 保存由本地后端授权状态决定，CLI、MCP 和网页客户端不得传入或伪造 `is_pro`。

## HTTP

`GET /api/state?token=TOKEN` 返回 `projects: {active, items}`、`scenes`（与 `ProjectStore.scene_public()` 相同的 `{project, active, saved, saved_count, free_limit, draft}` 形状）以及 `project_event`、`project_message`。场次命令也使用 `project_event` 确认完成。TOKEN 只从本机 `runtime/connection.json` 读取，不写进共享脚本、MCP 返回值或日志。

`POST /api/control?token=TOKEN`，Content-Type 为 application/json：

```json
{"type":"project_switch","id":"steamship"}
```

其他命令：`project_save`；`project_create` 携带 name、description、source；`project_update` 携带 id、name、description。name 最长 80 字符，description 最长 2000 字符。返回入队成功不等于保存完成，需轮询状态，等 project_event 增加，或检查 error；CLI 已实现等待确认。多人并发命令尚无逐请求关联，按单人操作设计。

场次命令：

```json
{"type":"scene_create","name":"第二场追逐","description":"出弯反超","discard_draft":false}
{"type":"scene_save"}
{"type":"scene_switch","id":"SCENE_ID","discard_draft":false}
{"type":"scene_delete","id":"SCENE_ID"}
{"type":"scene_discard","discard_draft":true}
```

Agent 客户端以现有的 `project_event` 确认场次命令完成，不把 HTTP `202` 或入队响应本身当作完成。后端失败时即使重复返回同一错误，也会优先抛出；超时后不要重复创建，先重新读取 `scenes`。

失败时当前窗口场景不切换。录制或导出期间拒绝项目操作。切换前自动保存源项目；成功后暂停取景，清空旧输入和旧下载列表，恢复目标项目录制镜头归属。文件快照仅含目标 Scene 及其依赖，其他缓存工程不会被打包进快照。

免费版仍可进行普通录制和导出，但导出带 `DKYJ DIRECTOR · PREVIEW` 水印；Pro 可去除水印。手柄识别、输入反馈和官方演示可用，正式项目的手柄运镜录制由 Pro 控制。手动关键帧与普通录制的具体权限由后端当前授权状态执行。

## AI 建模约定

以 `bpy.context.scene` 为当前工程，只在其集合内查找对象。不要用全局同名查找：缓存项目可能使 Blender 自动添加 .001 后缀。对象、网格和动作在复制时独立，已有源模型不重新生成。分区和角色元数据约定见 architecture.md。

## Creative briefs (0.6)

State includes `briefs: {revision, items}`. Data-only control commands: `brief_create` with a client-generated id, scene, characters, action, camera and source project id; `brief_reply` with id/message; `brief_update` with id/status/message and optional project_id/verification. Repeating brief_create with the same id is idempotent. These commands are processed on the Blender main thread and persisted to projects/briefs.json. A ready update needs an existing saved project and verification text. Use the optional MCP adapter rather than building an agent around raw HTTP credentials.
