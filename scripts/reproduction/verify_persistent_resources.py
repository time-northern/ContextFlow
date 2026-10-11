"""Verify the mounted checkpoint, dataset, and simulator without modifying them."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[2]
STORAGE = Path('/context-flow-storage/contextflow')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    if not STORAGE.parent.is_mount():
        raise SystemExit('File storage is not mounted: /context-flow-storage')
    manifest = json.loads((STORAGE / 'logs/reproduction/checkpoint-manifest.sha256.json').read_text())
    checkpoint = STORAGE / 'checkpoints/ContextFlow/ContextFlow_run1/19999'
    for entry in manifest:
        path = checkpoint / entry['path']
        if not path.is_file() or sha256(path) != entry['sha256']:
            raise SystemExit('Checkpoint missing or changed: ' + str(path))
    print('Checkpoint SHA256: all 20 files match.', flush=True)
    dataset = STORAGE / 'datasets/physical-intelligence/libero'
    record = json.loads((STORAGE / 'logs/storage/dataset-download-verification.json').read_text())
    metadata = json.loads((dataset / 'meta/info.json').read_text())
    files = list((dataset / 'data').rglob('*.parquet'))
    if len(files) != metadata['total_episodes'] or len(files) != record['episodes']:
        raise SystemExit('Dataset file count is incomplete.')
    for entry in record['files']:
        path = dataset / entry['path']
        if not path.is_file() or path.stat().st_size != entry['bytes']:
            raise SystemExit('Dataset file missing or size changed: ' + str(path))
    print(f'Dataset: {len(files)} episodes; every recorded file size matches.', flush=True)
    tokenizer = STORAGE / 'assets/openpi/big_vision/paligemma_tokenizer.model'
    if not tokenizer.is_file() or tokenizer.stat().st_size != 4264023:
        raise SystemExit('Tokenizer is missing or incomplete.')
    for name, target in [('checkpoints', 'checkpoints'), ('logs', 'logs'),
                         ('output', 'outputs'), ('datasets', 'datasets')]:
        if (REPO / name).resolve() != STORAGE / target:
            raise SystemExit('Repository link differs: ' + name)
    env = dict(os.environ, LIBERO_CONFIG_PATH=str(STORAGE / 'configs/libero'), MUJOCO_GL='egl')
    subprocess.run([str(REPO / 'examples/libero/.venv/bin/python'), '-c',
                    'import sys,numpy,mujoco,libero; print("Simulator imports:",sys.version.split()[0])'],
                   check=True, env=env)
    print('Persistent resource checks passed. No /app restoration was needed.')


if __name__ == '__main__':
    main()
