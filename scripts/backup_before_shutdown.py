"""Compatibility entry point; runtime files now persist directly on file storage."""
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[1]
print('权重、数据集、日志和视频已直接存入文件存储，无需复制 /app。', flush=True)
subprocess.run([sys.executable, str(repo / 'scripts/reproduction/verify_persistent_resources.py')], check=True)
