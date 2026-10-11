"""Restore the exact public dataset revision used in the completed evaluation."""
import os
from pathlib import Path
from huggingface_hub import snapshot_download

revision = 'a4336d589d589045d1c56423ffdf3b88a0e19b1f'
root = Path(os.environ['LEROBOT_HOME']) / 'physical-intelligence/libero'
snapshot_download('physical-intelligence/libero', repo_type='dataset', revision=revision,
                  local_dir=root, allow_patterns=['meta/*', 'data/*'], max_workers=8)
print('Dataset restored:', root, 'revision:', revision)
