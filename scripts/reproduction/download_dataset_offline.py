"""Run on a local computer; no GPU or running Bitahub machine is required.

Install: python -m pip install huggingface_hub
Download: python download_dataset_offline.py --output ./libero
Then upload the contents to contextflow/datasets/physical-intelligence/libero/ via WebDAV.
"""
import argparse
import json
from pathlib import Path

REVISION = 'a4336d589d589045d1c56423ffdf3b88a0e19b1f'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('libero'))
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not args.verify_only:
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id='physical-intelligence/libero', repo_type='dataset',
                          revision=REVISION, local_dir=args.output,
                          allow_patterns=['meta/*', 'data/*'], max_workers=8)
    metadata = json.loads((args.output / 'meta/info.json').read_text())
    files = list((args.output / 'data').rglob('*.parquet'))
    if len(files) != metadata['total_episodes'] or any(p.stat().st_size == 0 for p in files):
        raise SystemExit(f'Incomplete dataset: {len(files)}/{metadata["total_episodes"]} episodes')
    print('Ready to upload:', args.output.resolve())
    print('Dataset revision:', REVISION, '; episodes:', len(files))
    print('WebDAV target (relative to storage root): contextflow/datasets/physical-intelligence/libero/')
    print('Upload meta/ and data/ with all subfolders. Download caches do not need uploading.')


if __name__ == '__main__':
    main()
