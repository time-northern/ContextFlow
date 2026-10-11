#!/usr/bin/env bash
# Compatibility entry point: resources now live directly on persistent storage.
set -euo pipefail
cd /root/ContextFlow
source env.sh
.venv/bin/python scripts/setup_storage.py
.venv/bin/python scripts/reproduction/verify_persistent_resources.py
