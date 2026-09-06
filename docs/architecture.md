# 架构

浏览器通过带配对 token 的 HTTP JSON 命令控制 Blender 主线程。PNG 画面来自 GPU 离屏绘制。网页不能提交 Python 代码；可选 MCP 是单独的本地工具接口。

ProjectStore 将项目目录与 Scene 缓存分开管理。切换时加载已有 .blend 库中的 Scene，再赋给活动窗口。对象自动重命名时更新角色引用与录制摄影机引用。保存仅写目标 Scene 及依赖，原文件保留一份 previous 备份。修改内存后应显式保存；无定时全量自动保存。

空间总览是独立辅助 Scene：共享原始角色与物体，另建分区地板、标注、视锥和观察摄影机。辅助场景在写文件前清理。GPU 绘制回调不创建/删除 Scene、不强制切帧，避免绘制锁死。

导出由独立 Blender 后台进程读取镜头快照。先渲染纯镜头，再逐帧采样并烘焙总览摄影机模型、视锥和观察机位关键帧。Pillow 生成中文图例，Blender VSE 合成视频。macOS 使用系统中文字体，Windows 使用 Microsoft YaHei 等中文字体；也可通过 DKYJ_FONT 指向本机字体文件。服务器与 HTTPS 证书共用 network_utils 的局域网地址选择，支持 DKYJ_LAN_IP。

## 场景元数据

- `previs_title` / `previs_subtitle`：标题与一句话简报。
- `previs_zones`：JSON 分区列表，id/name/description/color/x/y/z/width/depth/height/open_sky，Blender 单位；界面换算米。
- `previs_story`：动作时间段；`previs_subjects`：角色 id、object、color、name、description。
- `previs_zone_id`：已有地板所属分区；`previs_overview_hide`：总览隐藏实体/改轮廓。
- `previs_bounds_ignore`：不参与场景范围，例如海面。
- `previs_ai_hide` / `previs_ai_show`：简化人物导出时切换显示。
- `previs_last_take`：当前项目录制镜头名；`dkyj_saved_name` 用于跨项目加载时重映射名称。

所有文件都在本机；程序不自动上传、调用付费模型、收集遥测或发布项目。安装器只安装本仓库插件；若另行安装 MCP，其隐私与访问控制由该插件管理。
