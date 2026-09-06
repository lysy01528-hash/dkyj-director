# 项目接口 · v0.5

Windows: replace `.venv/bin/python` with `.venv\Scripts\python.exe`; use `py -3` instead of `python3`. Phone support is iPhone Safari only. See [Windows setup](windows.md).

接口服务由 Blender 插件启动，所有模型读写在 Blender 主线程执行。自然语言的理解由外部助手负责；网页保存描述，不内置文本生成模型。切换只载入存储的场景。

## CLI

在仓库根目录、导演台运行时执行：

```sh
.venv/bin/python scripts/projects.py list
.venv/bin/python scripts/projects.py save
.venv/bin/python scripts/projects.py switch --id steamship
.venv/bin/python scripts/projects.py create --name '蒸汽船第二方案' --description '复用船舱和甲板，调整人物出舱节奏' --source current
.venv/bin/python scripts/projects.py update --id PROJECT_ID --name '新名称' --description '新的场景简报'
```

`list` 返回活动项目及项目 id、名称、描述、更新时间和可用状态。助手先读取列表，匹配用户描述，再使用 id。不得仅因名称相似覆盖已有项目。`create` 的 source 可为 current 或列表里的 id，创建后自动切入；随后通过 Blender MCP 或 Blender 编辑当前场景，再执行 save。

## HTTP

`GET /api/state?token=TOKEN` 返回 `projects: {active, items}` 和 `project_event`、`project_message`。TOKEN 从本机 `runtime/connection.json` 读取，不写进共享脚本。

`POST /api/control?token=TOKEN`，Content-Type 为 application/json：

```json
{"type":"project_switch","id":"steamship"}
```

其他命令：`project_save`；`project_create` 携带 name、description、source；`project_update` 携带 id、name、description。name 最长 80 字符，description 最长 2000 字符。返回入队成功不等于保存完成，需轮询状态，等 project_event 增加，或检查 error；CLI 已实现等待确认。多人并发命令尚无逐请求关联，按单人操作设计。

失败时当前窗口场景不切换。录制或导出期间拒绝项目操作。切换前自动保存源项目；成功后暂停取景，清空旧输入和旧下载列表，恢复目标项目录制镜头归属。文件快照仅含目标 Scene 及其依赖，其他缓存工程不会被打包进快照。

## AI 建模约定

以 `bpy.context.scene` 为当前工程，只在其集合内查找对象。不要用全局同名查找：缓存项目可能使 Blender 自动添加 .001 后缀。对象、网格和动作在复制时独立，已有源模型不重新生成。分区和角色元数据约定见 architecture.md。

## Creative briefs (0.6)

State includes `briefs: {revision, items}`. Data-only control commands: `brief_create` with a client-generated id, scene, characters, action, camera and source project id; `brief_reply` with id/message; `brief_update` with id/status/message and optional project_id/verification. Repeating brief_create with the same id is idempotent. These commands are processed on the Blender main thread and persisted to projects/briefs.json. A ready update needs an existing saved project and verification text. Use the optional MCP adapter rather than building an agent around raw HTTP credentials.
