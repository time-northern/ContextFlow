# CPU / GPU code synchronization

Repository: https://github.com/time-northern/contex-flow-base

## First clone on each machine

```bash
git clone --recurse-submodules https://github.com/time-northern/contex-flow-base.git ContextFlow
cd ContextFlow
```

If the repository is private, authenticate to GitHub on each machine first.
For an existing clone, initialize the pinned LIBERO submodule with:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

## Send changes from the CPU machine

Review the files before committing:

```bash
git status --short
git diff
git add <changed-files>
git commit -m "Describe the change"
git push origin main
```

## Receive changes on the GPU machine

Run these commands before starting a new inference process:

```bash
git status --short
git pull --ff-only origin main
git submodule sync --recursive
git submodule update --init --recursive
git rev-parse HEAD
```

Resolve or commit local edits before pulling. If both machines create commits,
reconcile the histories before pushing; do not force-push to synchronize them.
The commit printed by `git rev-parse HEAD` identifies the code used for a run.
An inference process already running must be restarted to load the new code.

## Machine-local resources

Git synchronizes source, scripts, documentation, and dependency definitions.
Virtual environments, checkpoints, datasets, caches, logs, and inference output
remain outside version control and must be installed or provisioned separately.
Keep credentials in environment variables or an ignored `.env` file.

`env.sh`, `scripts/setup_storage.py`, and the storage recovery scripts describe
the existing Bitahub host and require its `/context-flow-storage` mount and
local runtime setup. A fresh clone does not recreate those resources. See
`ENVIRONMENT_SETUP.md` and `STORAGE_LAYOUT.md` before using these scripts on
another machine. The original model dependencies are in `pyproject.toml` and
`uv.lock`; LIBERO has a separate environment under `examples/libero`.
