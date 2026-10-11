"""Check persistent resources; --reference replays the original /app experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def check(reference_path):
    reference = json.loads(reference_path.read_text())
    print('重启前记录时间：', reference['created_at'])
    marker = Path(reference['marker_path'])
    marker_matches = marker.is_file() and sha256(marker) == reference['marker_sha256']
    print('/app 测试标记：', '保留且内容一致' if marker_matches else '缺失或内容变化')
    missing, changed = [], []
    for entry in reference['critical_files']:
        path = Path(entry['path'])
        if not path.is_file():
            missing.append(str(path))
        elif path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            changed.append(str(path))
    print('关键文件：', len(reference['critical_files']), '个；缺失：', len(missing), '个；变化：', len(changed), '个')
    dataset = Path(reference['dataset_path'])
    episodes = list((dataset / 'data').rglob('*.parquet'))
    dataset_matches = (len(episodes) == reference['dataset_episode_count'] and
                       sum(p.stat().st_size for p in episodes) == reference['dataset_episode_bytes'])
    print('数据集 Parquet：', len(episodes), '/', reference['dataset_episode_count'], '；数量及总大小：', '一致' if dataset_matches else '不一致')
    mount_lines = [line for line in Path('/proc/self/mountinfo').read_text().splitlines()
                   if len(line.split()) > 4 and line.split()[4] == '/app']
    print('/app 挂载来源：', mount_lines[0] if mount_lines else '未检测到独立挂载')
    print('挂载记录与重启前：', '一致' if mount_lines == reference['app_mountinfo'] else '不同')
    for path in missing + changed:
        print('需检查：', path)
    if marker_matches and not missing and not changed and dataset_matches:
        print('结论：当前 /app 与参考记录一致：标记、关键文件和数据集文件数量/总大小均通过检查。')
        print('这不能保证删除、重建或后续其他操作也保留 /app。')
        return 0
    print('结论：/app 未通过保留检查。请先保存此输出，再根据缺失情况恢复。')
    print('恢复命令：bash /root/ContextFlow/scripts/restore_after_shutdown.sh')
    return 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    if args.reference is None:
        verifier = Path(__file__).resolve().parent / 'reproduction/verify_persistent_resources.py'
        result = subprocess.run([sys.executable, str(verifier)])
        raise SystemExit(result.returncode)
    if not args.reference.is_file():
        parser.error('原始重启测试参考记录不存在，请确认文件存储已挂载：' + str(args.reference))
    raise SystemExit(check(args.reference))
