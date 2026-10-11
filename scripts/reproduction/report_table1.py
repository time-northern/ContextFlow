"""Compare a completed, exception-free official evaluation with paper Table 1."""
import json
import math
from pathlib import Path
import sys


def wilson(successes, n):
    z = 1.959963984540054
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [center - half, center + half]


def main():
    root = Path(sys.argv[1])
    protocol = json.loads((root / 'protocol.json').read_text())
    expected = {t['task']: t for t in protocol['tasks']}
    rows = []
    for suite in ('libero_spatial', 'libero_object'):
        log = (root / f'{suite}.log').read_text(errors='replace')
        if 'Caught exception:' in log or 'Traceback (most recent call last)' in log:
            raise SystemExit(f'{suite}: runtime errors invalidate this comparison')
        result = json.loads((root / f'{suite}.json').read_text())
        if result['config']['seed'] != protocol['seed']:
            raise SystemExit('Seed differs from recorded protocol')
        for t in result['per_task_results']:
            ref = expected[t['task_description']]
            n, k = t['episodes'], t['successes']
            if n != protocol['trials_per_task']:
                raise SystemExit('Incomplete trial count')
            rows.append({**ref, 'episodes': n, 'successes': k,
                         'observed_success_rate': k / n,
                         'difference_percentage_points': 100 * (k / n - ref['paper_success_rate']),
                         'wilson_95_interval': wilson(k, n)})
    if len(rows) != 4 or len({r['task'] for r in rows}) != 4:
        raise SystemExit('Expected exactly four distinct tasks')
    k = sum(r['successes'] for r in rows)
    n = sum(r['episodes'] for r in rows)
    suite_results = {}
    for suite in ('libero_spatial', 'libero_object'):
        selected = [r for r in rows if r['suite'] == suite]
        suite_n = sum(r['episodes'] for r in selected)
        suite_k = sum(r['successes'] for r in selected)
        suite_results[suite] = {'episodes': suite_n, 'successes': suite_k, 'observed_success_rate': suite_k / suite_n, 'paper_success_rate': sum(r['paper_success_rate'] for r in selected) / len(selected)}
    protocol['status'] = 'completed 200 rollouts without reported runtime exceptions'
    (root / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    summary = {'protocol': protocol, 'results': rows,
               'suite_results': suite_results,
               'total_episodes': n, 'total_successes': k,
               'overall_success_rate': k / n,
               'paper_overall_success_rate': sum(t['paper_success_rate'] for t in expected.values()) / 4,
               'interpretation': '本次使用单个公开 checkpoint 和评测种子，验证推理评测的可复现性；不包含独立重新训练，不能单独判断整篇论文的真实性。'}
    (root / 'comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
    text = ['# ContextFlow：LIBERO 主表推理复现', '',
            '使用作者公开的 `ContextFlow_run1/19999` 权重，仿真种子 7、模型初始随机种子 0。每任务 50 次，4 个任务共 200 次。',
            '', '论文：[Table 1](https://arxiv.org/html/2609.06852v1)。运行版本与配置见本目录 `protocol.json`，本地代码修改见 `local-code-changes.patch`。', '',
            '| 任务 | 论文 | 本次 | 成功次数 | 差值（百分点） | Wilson 95% 区间 |',
            '| --- | ---: | ---: | ---: | ---: | ---: |']
    table_order = {t['task_index']: i for i, t in enumerate(protocol['tasks'])}
    for r in sorted(rows, key=lambda r: table_order[r['task_index']]):
        lo, hi = r['wilson_95_interval']
        text.append(f"| {r['task']} | {100*r['paper_success_rate']:.1f}% | {100*r['observed_success_rate']:.1f}% | {r['successes']}/{r['episodes']} | {r['difference_percentage_points']:+.1f} | {100*lo:.1f}–{100*hi:.1f}% |")
    for suite, r in suite_results.items():
        text.append(f"| {suite} average | {100*r['paper_success_rate']:.1f}% | {100*r['observed_success_rate']:.1f}% | {r['successes']}/{r['episodes']} | {100*(r['observed_success_rate']-r['paper_success_rate']):+.1f} | — |")
    text += ['', f'总体：{k}/{n} = {100*k/n:.1f}%；论文为 73.5%。', '', '上述区间反映每任务 50 次试验的统计不确定性，不包含训练种子、示范选择或版本变化的影响。', '', summary['interpretation'], '']
    (root / 'comparison.md').write_text('\n'.join(text))
    print('\n'.join(text))


if __name__ == '__main__':
    main()
