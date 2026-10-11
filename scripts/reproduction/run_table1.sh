#!/usr/bin/env bash
set -euo pipefail
cd /root/ContextFlow
source env.sh
run_name="${1:-table1_run1_seed7_$(date +%Y%m%d_%H%M%S)}"
if [[ ! "$run_name" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo 'Run name must contain only letters, numbers, underscores or hyphens.' >&2
  exit 2
fi
run_dir="logs/reproduction/$run_name"
mkdir "$run_dir"
cp logs/reproduction/protocol.json "$run_dir/protocol.json"
.venv/bin/python - <<'PY'
import socket
with socket.socket() as s:
    if s.connect_ex(('127.0.0.1', 8000)) == 0:
        raise SystemExit('Port 8000 is already in use; stop the existing policy server first.')
PY
.venv/bin/python -u scripts/serve_policy.py policy:checkpoint \
  --policy.inference_dtype=float32 --policy.local-files-only --policy.config=ContextFlow \
  --policy.dir=checkpoints/ContextFlow/ContextFlow_run1/19999 \
  > "$run_dir/server.log" 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true; wait "$server_pid" 2>/dev/null || true' EXIT
printf '%s\n' "$server_pid" > "$run_dir/server.pid"
.venv/bin/python - "$server_pid" <<'PY'
import os, sys, time
from websockets.sync.client import connect
pid = int(sys.argv[1])
for _ in range(600):
    os.kill(pid, 0)
    try:
        with connect('ws://127.0.0.1:8000', open_timeout=2, close_timeout=2) as connection:
            connection.recv()
        break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit('Policy server did not become ready within 10 minutes.')
PY
for suite in libero_spatial libero_object; do
  examples/libero/.venv/bin/python -u examples/libero/main_incontext.py \
    --host 127.0.0.1 --task-suite-name "$suite" --num-trials-per-task 50 --seed 7 \
    --results-out-path "$run_dir/$suite.json" \
    --video-out-path "output/reproduction/$run_name/$suite" \
    > "$run_dir/$suite.log" 2>&1
  if grep -q 'Caught exception:' "$run_dir/$suite.log"; then
    echo "Infrastructure error detected in $suite; this run must not be used as a policy success-rate result." >&2
    exit 1
  fi
done
.venv/bin/python scripts/reproduction/report_table1.py "$run_dir"
