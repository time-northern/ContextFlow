"""Resume the public checkpoint identified in logs/reproduction/checkpoint-files.json."""

import concurrent.futures
import hashlib
import json
import logging
from pathlib import Path

import gdown
import requests


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    root = Path("checkpoints/ContextFlow/ContextFlow_run1/19999").resolve()
    root.mkdir(parents=True, exist_ok=True)
    files = json.loads(Path("logs/reproduction/checkpoint-files.json").read_text())
    original_request = requests.sessions.Session.request

    def bounded_request(self, *args, **kwargs):
        kwargs.setdefault("timeout", 90)
        return original_request(self, *args, **kwargs)

    requests.sessions.Session.request = bounded_request

    def download(entry):
        target = (root / entry["path"]).resolve()
        if not target.is_relative_to(root):
            raise ValueError("Checkpoint path is outside its destination")
        if target.with_name(target.name + ".aria2").exists():
            raise RuntimeError("An aria2 download is incomplete: " + entry["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Downloading %s", entry["path"])
        result = gdown.download(
            id=entry["id"], output=str(target), quiet=True, resume=True, use_cookies=False
        )
        if result is None:
            raise RuntimeError("Download failed: " + entry["path"])
        digest = hashlib.sha256()
        with target.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
        result = {**entry, "bytes": target.stat().st_size, "sha256": digest.hexdigest()}
        logging.info("Complete %s (%d bytes)", entry["path"], result["bytes"])
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(download, files))
    Path("logs/reproduction/checkpoint-manifest.sha256.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )
    logging.info("CHECKPOINT DOWNLOAD COMPLETE: %d bytes", sum(x["bytes"] for x in results))


if __name__ == "__main__":
    main()
