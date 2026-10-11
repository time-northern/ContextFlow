# ContextFlow 持久化目录

项目代码和已安装的两个虚拟环境位于 `/root/ContextFlow`；大文件及运行资源直接使用
`/context-flow-storage/contextflow`。旧备份层级及其软链接已移除。

| 持久化目录 | 内容 | 项目访问方式 |
| --- | --- | --- |
| `checkpoints/` | run1/19999 模型权重 | `checkpoints` 软链接 |
| `datasets/` | 完整 LIBERO 数据集及 LIBERO 原始数据目录 | `datasets` 软链接、`LEROBOT_HOME` |
| `outputs/` | 正式评测与试跑视频 | `output` 软链接 |
| `logs/reproduction/` | 论文、协议、评测 JSON、报告和下载来源记录 | `logs` 软链接 |
| `logs/setup/` | 最初环境验证记录 | `logs` 软链接 |
| `logs/storage/` | 存储迁移、重启测试、数据下载及完整性检查记录 | `logs` 软链接 |
| `runtimes/python/` | Python 3.8 解释器 | 仿真虚拟环境的解释器链接 |
| `assets/openpi/` | 分词器 | `OPENPI_DATA_HOME` |
| `configs/libero/` | LIBERO 路径配置 | `LIBERO_CONFIG_PATH` |
| `configs/vnc/` | VNC 启动脚本副本 | 保留配置 |
| `environment/requirements/` | 模型与仿真依赖安装/锁定清单 | 按需安装 |
| `environment/system-state/` | 原软件包版本、Git 提交及修改补丁 | 环境记录 |
| `environment/huggingface-hub/` | 原数据版本引用记录 | 环境记录 |
| `tools/` | 本地下载辅助脚本 | 可通过 WebDAV 获取 |

完整 LIBERO 为 1693 个 Parquet、273465 帧，数据版本固定为
`a4336d589d589045d1c56423ffdf3b88a0e19b1f`。
原备份的 4 条示范与 4 份元信息已核对 SHA256 后合并到完整数据集，未保留重复副本。
旧下载元信息及原校验清单作为历史记录保存在 `logs/storage/`；其中旧路径代表当时状态，
当前文件位置可通过 `logs/storage/layout-migration-verification.json` 的映射查找。

## 使用

```bash
cd /root/ContextFlow
source env.sh
```

权重、视频、日志、解释器和分词器都直接使用持久化文件，无需每次开机复制回 `/app`。
`/app/contextflow/uv-cache` 和 `/app/contextflow/huggingface` 仅用于可重建的安装/Arrow 缓存。
同一文件存储须继续挂载在 `/context-flow-storage`；未挂载时 `env.sh` 会报错。

检查运行资源：

```bash
.venv/bin/python scripts/reproduction/verify_persistent_resources.py
```

如以后项目链接被改动，可重新连接：

```bash
.venv/bin/python scripts/setup_storage.py
```

旧 `restore_after_shutdown.sh` 入口现在只重新连接并校验，不再复制文件。
旧 `backup_before_shutdown.py` 入口现在只校验运行资源，不再创建另一份备份。
`check_reboot_storage.py` 默认检查持久化运行资源；如需复查历史 `/app` 测试：

```bash
python3 scripts/check_reboot_storage.py --reference logs/storage/reboot-test-reference.json
```

历史 `/app` 参考路径已不存在是已知事实，不表示当前持久化文件丢失。

数据补齐命令（当前完整，无需重复运行）：

```bash
.venv/bin/python scripts/reproduction/download_dataset.py
```

目录调整后的验证：权重 SHA256、1693 个数据文件大小、两个环境依赖均通过；
实际 LIBERO 仿真观测与 3 次真实模型推理通过，动作形状为 50×7，全部有限。
验证记录位于 `logs/storage/layout-validation-20261010_231103/`。
