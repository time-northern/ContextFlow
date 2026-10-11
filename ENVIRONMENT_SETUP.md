# 本机 ContextFlow 环境

**Bitahub 存储实测：2026-10-10 本次重启清空了 `/app`，系统盘 `/root` 保留。关机前请先阅读 [BITAHUB_STORAGE.md](BITAHUB_STORAGE.md)。关键备份现已迁移至文件存储，完整数据集也已补齐到文件存储。**

资源现直接使用文件存储，布局见 [STORAGE_LAYOUT.md](STORAGE_LAYOUT.md)。
权重、日志、视频、Python 3.8、分词器与配置均无需恢复到 `/app`。
完整数据集已补齐到 `datasets/physical-intelligence/libero/`。

仓库：`https://github.com/dingjiansw101/ContextFlow`

固定提交：`c6dee891f0afd520aec5a8869891e9b06b99f856`。
LIBERO 子模块：`f78abd68ee283de9f9be3c8f7e2a9ad60246e95c`。
LeRobot 使用原始 `uv.lock` 指定的 `6674e368249472c91382eb54bb8501c94c7f0c56`。

## 打开新终端后

```bash
cd /root/ContextFlow
source env.sh
```

`env.sh` 设置持久化资源路径、临时缓存、LIBERO 路径、EGL 渲染和 float32 推理精度。
它会在当前 shell 中取消继承的 localhost:7897 代理，因为该代理对 GitHub 的 TLS 连接失败。
没有修改 Conda base、shell 启动文件或 NVIDIA 驱动。

## 两个 Python 环境

模型、训练及策略服务器：

```bash
source .venv/bin/activate
python scripts/serve_policy.py --help
```

LIBERO 客户端使用独立的 Python 3.8；可以直接指定解释器，避免激活错环境：

```bash
examples/libero/.venv/bin/python examples/libero/main_incontext.py --help
```

主环境的依赖版本来自原始 `uv.lock`，通过镜像安装精确版本。
旧版 `pyav==14.0.1` 使用锁文件中的官方 wheel URL 和 SHA256。
导出的安装清单位于 `/context-flow-storage/contextflow/environment/requirements/model-requirements.lock.txt` 和
`/context-flow-storage/contextflow/environment/requirements/model-requirements.install.txt`。

LIBERO 客户端使用 `torch==1.11.0+cpu`、`torchvision==0.12.0+cpu`、
`torchaudio==0.11.0+cpu`，其余依赖沿用项目版本。
CPU 构建用于加载仿真初始状态；策略模型由主环境在 GPU 上运行，MuJoCo 使用 NVIDIA EGL 渲染。
CPU 安装清单位于 `/context-flow-storage/contextflow/environment/requirements/libero-requirements.cpu.txt`，没有修改项目的原始 requirements 文件。

## 存储路径

系统盘约 30 GB，临时卷挂载于 `/app`。以下缓存和产物使用临时卷：

| 内容 | 路径 |
| --- | --- |
| uv 缓存 | `/app/contextflow/uv-cache` |
| uv 下载的 Python | `/context-flow-storage/contextflow/runtimes/python` |
| Hugging Face 缓存 | `/app/contextflow/huggingface` |
| LeRobot 数据集 | `/context-flow-storage/contextflow/datasets` |
| openpi 预训练缓存 | `/context-flow-storage/contextflow/assets/openpi` |
| 模型权重 | `checkpoints` → `/context-flow-storage/contextflow/checkpoints` |
| 评测及试跑视频 | `output` → `/context-flow-storage/contextflow/outputs` |
| 日志 | `logs` → `/context-flow-storage/contextflow/logs` |
| LIBERO 路径配置 | `/context-flow-storage/contextflow/configs/libero/config.yaml` |

安装的系统依赖为 `libegl1`、`libgles2`，以及下载工具 `aria2`。

## 论文评测资源

原评测时完整 LIBERO 数据已下载并通过项目的数据加载器校验：1693 个 episode、273465 帧、40 个任务。
该完整数据集在重启时丢失，现已按同一版本完整下载到文件存储并通过文件数量、总帧数及大小核验。
数据固定在 Hugging Face 提交 `a4336d589d589045d1c56423ffdf3b88a0e19b1f`；路径为
`/context-flow-storage/contextflow/datasets/physical-intelligence/libero`。

作者公开的 run1、step 19999 权重已下载并完成 Orbax 参数恢复，路径：

```text
checkpoints/ContextFlow/ContextFlow_run1/19999
```

模型服务器（一个终端）：

```bash
cd /root/ContextFlow
source env.sh
.venv/bin/python scripts/serve_policy.py policy:checkpoint \
  --policy.inference_dtype=float32 \
  --policy.local-files-only \
  --policy.config=ContextFlow \
  --policy.dir=checkpoints/ContextFlow/ContextFlow_run1/19999
```

LIBERO 评测（另一个终端）：

```bash
cd /root/ContextFlow
source env.sh
examples/libero/.venv/bin/python examples/libero/main_incontext.py \
  --host 127.0.0.1 \
  --task-suite-name libero_spatial \
  --num-trials-per-task 50 \
  --results-out-path logs/eval_results/unseen/libero_spatial.json
```

## 显存限制

本机为 RTX 4090（24 GB）。项目 README 给出的推理需求为 >16 GB，
LoRA 微调需求为 >40 GB。默认训练 batch size 为 32，不能视为已经适配本机。
正式训练前需要另行验证较小 batch、模型配置和显存占用，或使用更大显存 GPU。

## 已完成的模型环境验证

- Python 3.11.15，JAX 0.5.0，PyTorch 2.6.0（CUDA 12.4），Flax 0.10.2。
- JAX 与 PyTorch 都已在 RTX 4090 上完成实际 GPU 矩阵运算。
- 策略服务器、训练、归一化脚本的 `--help` 均可运行。
- 25 项关键测试通过。
- 最初安装时 `uv sync --locked --offline` 已通过（现在下载缓存可丢弃），原始 `pyproject.toml` 和 `uv.lock` 未修改。
- 版本清单与结果保存在 `logs/setup/model-freeze.txt`、`logs/setup/model-verification.json` 和 `logs/setup/pytest.log`。

## 已完成的 LIBERO 验证

- Python 3.8.20、PyTorch 1.11.0+cpu、NumPy 1.22.4、MuJoCo 3.2.3、robosuite 1.4.1。
- `uv pip check` 通过；`main_incontext.py --help` 可运行。
- 已创建 `libero_spatial` 第一个任务，加载 50 组初始状态中的第一组，执行 5 步仿真。
- 两个相机均成功使用 EGL 输出非空的 128×128 RGB 图像，PNG 和 MP4 保存成功。
- 图像、视频和结果位于 `logs/setup/libero-smoke.png`、`logs/setup/libero-smoke.mp4`、`logs/setup/libero-verification.json`。
- 完整客户端版本清单：`logs/setup/libero-freeze.txt` 与 `/context-flow-storage/contextflow/environment/requirements/libero-requirements.lock.txt`。
- 重跑检查：先 `source env.sh`，再运行 `examples/libero/.venv/bin/python logs/setup/check-libero-environment.py`。
- 构建 `egl-probe` 时需要 CMake；已通过临时添加主环境 `.venv/bin` 到构建命令的 PATH 完成编译。

## 复现主表的完整评测

先停止手动启动的策略服务器，然后运行：

```bash
cd /root/ContextFlow
bash scripts/reproduction/run_table1.sh
```

该脚本启动全新策略服务器（模型随机种子 0），按 `libero_spatial`、`libero_object` 顺序
评测 4 个未见任务，每任务 50 次，仿真种子 7。使用项目原始评测脚本和默认示范选择逻辑。
每次运行在 `logs/reproduction/table1_run1_seed7_<时间>/` 保存服务器日志、仿真日志、
两个套件的 JSON 和最终 `comparison.md` / `comparison.json`；视频位于
`output/reproduction/<同名运行>/`。若日志出现运行异常，脚本停止并拒绝生成有效比较。

运行版本、任务、论文主表目标成功率与精度设置记录于 `logs/reproduction/protocol.json`。
本次复现使用作者公开权重，不包含从头训练；单个 checkpoint、单个种子的结果
用于检验推理结果能否复现，不能单独判断论文是否存在学术不端。

策略服务器新增 `--policy.local-files-only`，将数据配置中的 `local_files_only` 设为 true，
直接读取已下载的同一数据集，避免 Hugging Face IP 限流和在线版本变化；模型参数及前处理算法未改变。
下载清单及本次文件的 SHA256 记录于 `logs/reproduction/checkpoint-manifest.sha256.json`。

评测脚本在每个任务结束后显式执行 `env.close()`，释放 EGL 资源，避免解释器退出时
出现 `EGL_NOT_INITIALIZED` 清理异常；试验循环、初始状态和成功判定保持原样。

## 已完成的论文主表评测

已使用作者公开的 `ContextFlow_run1/19999` 权重完成真实推理与 200 次 LIBERO 评测。
仿真种子为 7，模型初始随机种子为 0，每个任务使用官方提供的 50 个初始状态。

| 任务 | 论文 Table 1 | 本次评测 |
| --- | ---: | ---: |
| 饼干盒上的黑碗 → 盘子 | 86% | 96%（48/50） |
| 盘子旁的黑碗 → 盘子 | 42% | 34%（17/50） |
| 牛奶 → 篮子 | 76% | 82%（41/50） |
| 番茄酱 → 篮子 | 90% | 96%（48/50） |
| 总体 | 73.5% | 77.0%（154/200） |

空间套件为 65%（论文 64%），物体套件为 89%（论文 83%）。
200 次统计已逐任务对照 200 段视频文件；客户端和服务器日志没有运行异常。
首次真实模型调用含编译约 12.8 秒，后续两次调用约 0.16–0.18 秒。
运行时显存约 17 GB；评测结束后策略服务器已停止，显存已释放。

完整报告：[comparison.md](logs/reproduction/table1_run1_seed7_20261010_195844/comparison.md)。
正式 JSON、日志、协议、文件清单与核对结果位于同目录。
视频：`output/reproduction/table1_run1_seed7_20261010_195844/`。
论文：[Table 1](https://arxiv.org/html/2609.06852v1)。

本次验证公开权重的推理评测，不包含独立重新训练，不能单独判断整篇论文的真实性。

目录调整后的验证：权重 SHA256、1693 个数据文件大小、两个环境依赖均通过；
实际 LIBERO 仿真观测与 3 次真实模型推理通过，动作形状为 50×7，全部有限。
验证记录位于 `logs/storage/layout-validation-20261010_231103/`。
