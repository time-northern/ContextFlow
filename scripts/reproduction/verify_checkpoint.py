"""Check downloaded file sizes and record local SHA256 hashes before restoration."""
import hashlib
import json
from pathlib import Path

root = Path('checkpoints/ContextFlow/ContextFlow_run1/19999').resolve()
if list(root.rglob('*.aria2')) or list(root.rglob('*.part')):
    raise SystemExit('Checkpoint download is still incomplete')
expected_sizes = {x['path']: x['expected_bytes'] for x in json.loads(Path('logs/reproduction/checkpoint-public-urls.json').read_text())}
manifest = []
for entry in json.loads(Path('logs/reproduction/checkpoint-files.json').read_text()):
    path = (root / entry['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file() or not path.stat().st_size:
        raise SystemExit('Missing checkpoint file: ' + entry['path'])
    if entry['path'] in expected_sizes and path.stat().st_size != expected_sizes[entry['path']]:
        raise SystemExit('Unexpected checkpoint size: ' + entry['path'])
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    manifest.append({**entry, 'bytes': path.stat().st_size, 'sha256': digest.hexdigest()})
Path('logs/reproduction/checkpoint-manifest.sha256.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Checkpoint verified locally: {len(manifest)} files, {sum(x["bytes"] for x in manifest)} bytes')
print('Local hashes identify this download; they are not author-published reference hashes.')
