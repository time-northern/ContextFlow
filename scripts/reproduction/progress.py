"""Show completed official rollouts and runtime errors without interpreting partial rates."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('logs/reproduction') / Path('logs/reproduction/current-run.txt').read_text().strip()
rows = []
errors = []
for suite in ('libero_spatial', 'libero_object'):
    path = root / (suite + '.log')
    if not path.exists():
        continue
    text = path.read_text(errors='replace')
    task = None
    counts = Counter()
    successes = Counter()
    for line in text.splitlines():
        if line.startswith('Task: '):
            task = line[6:]
        if 'INFO:root:Success: ' in line and task is not None:
            counts[task] += 1
            successes[task] += line.endswith('True')
        if 'Caught exception:' in line:
            errors.append(line)
    rows.extend({'suite': suite, 'task': t, 'completed': counts[t], 'successes': successes[t]} for t in counts)
status = {'run': root.name, 'checked_at': datetime.now(timezone.utc).isoformat(), 'completed': sum(r['completed'] for r in rows), 'planned': 200, 'tasks': rows, 'runtime_errors': errors, 'finished': (root / 'comparison.json').exists()}
(root / 'progress.json').write_text(json.dumps(status, indent=2) + '\n')
print(json.dumps(status, ensure_ascii=False))
