# Bitahub 存储

2026-10-10 实测开发机重启后 `/app` 被清空，系统盘 `/root` 保留。
随后挂载文件存储 `context-flow-storage` 到 `/context-flow-storage`，并已完成资源整理。
权重、完整数据集、Python 3.8、分词器、配置、日志和视频现在直接使用文件存储。

当前目录与命令见 [STORAGE_LAYOUT.md](STORAGE_LAYOUT.md)。
原始重启前后证据、备份校验、迁移记录归入 `logs/storage/`。
原备份层级及其软链接已删除，今后无需恢复大文件到临时卷。

代码、两个虚拟环境的已安装包和主 Python `/opt/conda` 仍位于系统盘。
仿真虚拟环境的 Python 解释器现直接指向文件存储中的 `runtimes/python/`。
如果需要跨开发机保留系统依赖和安装环境，可以通过控制台保存开发镜像。
开发机关机与删除/停止不是相同操作；官方规定开发机关机超过 15 天会清理资源快照。

完整数据集已补齐并核验：1693 个 Parquet、273465 帧，34938730091 字节。
校验记录：`logs/storage/dataset-download-verification.json`。
无需重复备份可重建的 Arrow 和 uv 下载缓存。

WebDAV 可用于从本地访问文件存储；操作见 [WEBDAV_DATA_RESTORE.md](WEBDAV_DATA_RESTORE.md)。

官方说明：
- 开发机：https://www.bitahub.com/help/4001/4105/4117/
- 文件存储与 WebDAV：https://www.bitahub.com/help/4001/4103/4301/
