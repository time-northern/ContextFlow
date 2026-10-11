# WebDAV 数据上传

文件存储 `context-flow-storage` 挂载路径为 `/context-flow-storage`。
WebDAV 连接文件存储服务，无需通过开发机 SSH；尚未实测此账号关机时的 WebDAV 连接。

1. 在文件存储页面启用 WebDAV，获取服务地址并设置 WebDAV 专用账号密码。
2. 在本地 WebDAV 客户端填写该地址及专用账号。专用账号与平台登录账号不同。
3. 连接后可看到 `contextflow/checkpoints/`、`contextflow/datasets/`、`contextflow/logs/` 等目录。
   `nas://context-flow-storage` 是内部标识，不能替代 WebDAV 服务网址。

所有运行资源现在直接使用这些目录，布局见 [STORAGE_LAYOUT.md](STORAGE_LAYOUT.md)。
完整 LIBERO 当前已存在并核验，无需再下载或上传。
如未来需要补齐，可将 `contextflow/tools/download_dataset_offline.py` 保存到本地并执行：

```bash
python -m pip install huggingface_hub
python download_dataset_offline.py --output ./libero
```

上传本地 `libero` 内的 `meta/` 和 `data/` 至 WebDAV 根目录下：

```text
contextflow/datasets/physical-intelligence/libero/
```

不要额外套一层 `libero`，也不要仅上传未解压的压缩包。下载缓存无需上传。
WebDAV 负责文件传输，不会自动恢复被删除的文件。

下次开机后，继续将同一文件存储挂载到 `/context-flow-storage`，执行：

```bash
cd /root/ContextFlow
source env.sh
.venv/bin/python scripts/reproduction/verify_persistent_resources.py
```

运行资源无需复制回 `/app`。
数据集校验结果见 `logs/storage/dataset-download-verification.json`。

官方说明：https://www.bitahub.com/help/4001/4103/4301/
