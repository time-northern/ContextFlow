"""Connect the repository and simulator to the mounted persistent resources."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORAGE = Path('/context-flow-storage/contextflow')


def link(path, target):
    if path.is_symlink():
        if path.readlink() == target:
            return
        path.unlink()
    elif path.exists():
        raise SystemExit('Refusing to replace an ordinary file/directory: ' + str(path))
    path.symlink_to(target, target_is_directory=target.is_dir())


def main():
    if not STORAGE.parent.is_mount():
        raise SystemExit('File storage is not mounted: ' + str(STORAGE.parent))
    runtime = STORAGE / 'runtimes/python'
    executable = runtime / 'cpython-3.8.20-linux-x86_64-gnu/bin/python3.8'
    if not executable.is_file():
        raise SystemExit('Python 3.8 runtime is missing: ' + str(executable))
    for path in runtime.rglob('*'):
        if path.is_symlink():
            target = str(path.readlink())
            prefix = '/app/contextflow/python/'
            if target.startswith(prefix):
                destination = runtime / target[len(prefix):]
                path.unlink()
                path.symlink_to(os.path.relpath(destination, path.parent))
    for name, target in [('checkpoints', 'checkpoints'), ('logs', 'logs'),
                         ('output', 'outputs'), ('datasets', 'datasets')]:
        destination = STORAGE / target
        if not destination.is_dir():
            raise SystemExit('Persistent resource directory is missing: ' + str(destination))
        link(REPO / name, destination)
    venv = REPO / 'examples/libero/.venv'
    link(venv / 'bin/python', executable)
    config = venv / 'pyvenv.cfg'
    lines = config.read_text().splitlines()
    config.write_text('\n'.join('home = ' + str(executable.parent) if line.startswith('home = ')
                                else line for line in lines) + '\n')
    raw = STORAGE / 'datasets/libero-raw'
    legacy = STORAGE / 'outputs/libero-datasets'
    if legacy.is_dir() and not raw.exists():
        legacy.rename(raw)
    raw.mkdir(exist_ok=True)
    libero_config = STORAGE / 'configs/libero/config.yaml'
    text = libero_config.read_text()
    text = '\n'.join('datasets: "' + str(raw) + '"' if line.startswith('datasets:') else line
                     for line in text.splitlines()) + '\n'
    libero_config.write_text(text)
    print('Repository links and Python 3.8 now use persistent storage directly.')


if __name__ == '__main__':
    main()
