#!/usr/bin/env python3
"""Nature Frame Sync.

Syncs curated illustration collections to Home Assistant's /media mount.
The provider layer is intentionally small so mammals/insects/etc. can be
added later without changing the filesystem contract used by screensavers.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APP_VERSION = "0.1.0"
OPTIONS_PATH = Path("/data/options.json")
STATE_PATH = Path("/data/state.json")
MEDIA_ROOT = Path("/media/nature-frame")
USER_AGENT = f"NatureFrameSync/{APP_VERSION} (+Home Assistant)"
DOWNLOAD_WORKERS = 4


@dataclass(frozen=True)
class GithubTreeCollection:
    key: str
    title: str
    repo: str
    branch: str
    destination: str
    path_pattern: re.Pattern[str]


COLLECTIONS = {
    "inky_birds": GithubTreeCollection(
        key="inky_birds",
        title="Inky Bird Frame",
        repo="veteranbv/inky-bird-frame",
        branch="main",
        destination="birds",
        path_pattern=re.compile(
            r"^catalog/species/(?P<species>[^/]+)/(?P<variant>portrait|display)\.png$"
        ),
    ),
}


def log(message: str) -> None:
    print(f"[Nature Frame] {message}", flush=True)


def load_json(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def request(url: str, timeout: int = 45) -> urllib.response.addinfourl:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    return urllib.request.urlopen(req, timeout=timeout)


def fetch_json(url: str) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with request(url) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < 3:
                time.sleep(attempt * 2)
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def github_tree(collection: GithubTreeCollection) -> tuple[str, list[dict[str, Any]]]:
    branch_url = (
        f"https://api.github.com/repos/{collection.repo}/branches/{collection.branch}"
    )
    branch = fetch_json(branch_url)
    commit_sha = str(branch["commit"]["sha"])
    tree_sha = str(branch["commit"]["commit"]["tree"]["sha"])
    tree_url = (
        f"https://api.github.com/repos/{collection.repo}/git/trees/{tree_sha}"
        "?recursive=1"
    )
    tree = fetch_json(tree_url)
    if tree.get("truncated"):
        raise RuntimeError(f"GitHub returned a truncated tree for {collection.repo}")
    return commit_sha, list(tree.get("tree", []))


def selected_variants(orientation: str) -> set[str]:
    if orientation == "portrait":
        return {"portrait"}
    if orientation == "landscape":
        return {"display"}
    return {"portrait", "display"}


def output_orientation(variant: str) -> str:
    return "portrait" if variant == "portrait" else "landscape"


def safe_filename(species_dir: str) -> str:
    # Upstream names are already safe slugs such as 12942-eastern-bluebird.
    # Keep the taxon id in the filename to avoid any name collisions.
    return re.sub(r"[^A-Za-z0-9._-]+", "-", species_dir).strip("-") + ".png"


def download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=90) as response, tmp.open("wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
        if tmp.stat().st_size < 1024:
            raise RuntimeError(f"Downloaded file is unexpectedly small: {url}")
        os.replace(tmp, target)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def write_attribution(collection: GithubTreeCollection, root: Path) -> None:
    text = f"""Nature Frame collection: {collection.title}

Source repository: https://github.com/{collection.repo}
This folder is synchronized automatically by Nature Frame Sync.
Source images remain subject to the upstream project's licensing and provenance.
Do not edit synchronized image files here; local changes may be replaced.
"""
    (root / "SOURCE.txt").write_text(text, encoding="utf-8")


def sync_collection(
    collection: GithubTreeCollection,
    orientation: str,
    delete_removed: bool,
    state: dict[str, Any],
) -> dict[str, Any]:
    log(f"Checking {collection.title} ({orientation}) …")
    commit_sha, tree = github_tree(collection)
    variants = selected_variants(orientation)

    desired: dict[str, dict[str, str]] = {}
    for item in tree:
        path = str(item.get("path", ""))
        match = collection.path_pattern.match(path)
        if not match or match.group("variant") not in variants:
            continue
        folder = output_orientation(match.group("variant"))
        rel = f"{folder}/{safe_filename(match.group('species'))}"
        desired[rel] = {
            "path": path,
            "sha": str(item.get("sha", "")),
        }

    if not desired:
        raise RuntimeError(f"No images found in {collection.repo}; refusing to modify local media")

    root = MEDIA_ROOT / collection.destination
    root.mkdir(parents=True, exist_ok=True)
    write_attribution(collection, root)

    previous = state.get(collection.key, {})
    previous_files = previous.get("files", {}) if isinstance(previous, dict) else {}
    next_files: dict[str, str] = {}
    jobs: list[tuple[str, str, Path, str]] = []

    for rel, info in sorted(desired.items()):
        target = root / rel
        blob_sha = info["sha"]
        next_files[rel] = blob_sha
        if target.is_file() and previous_files.get(rel) == blob_sha:
            continue
        raw_url = (
            f"https://raw.githubusercontent.com/{collection.repo}/{commit_sha}/"
            f"{info['path']}"
        )
        jobs.append((rel, raw_url, target, blob_sha))

    if jobs:
        log(f"{collection.title}: downloading {len(jobs)} new/changed image(s) …")
        completed = 0
        failures: list[tuple[str, str]] = []
        with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as executor:
            futures = {
                executor.submit(download_file, url, target): rel
                for rel, url, target, _ in jobs
            }
            for future in as_completed(futures):
                rel = futures[future]
                try:
                    future.result()
                    completed += 1
                    if completed == 1 or completed % 10 == 0 or completed == len(jobs):
                        log(f"{collection.title}: {completed}/{len(jobs)} downloaded")
                except Exception as error:
                    failures.append((rel, str(error)))
                    log(f"WARNING: failed {rel}: {error}")

        failed_names = {rel for rel, _ in failures}
        for rel in failed_names:
            if rel in previous_files:
                next_files[rel] = previous_files[rel]
            else:
                next_files.pop(rel, None)
        if failures:
            log(f"WARNING: {len(failures)} image(s) will be retried next sync")
    else:
        log(f"{collection.title}: already up to date ({len(desired)} images)")

    if delete_removed:
        current_names = set(desired)
        for folder in ("portrait", "landscape"):
            directory = root / folder
            if not directory.exists():
                continue
            source_variant = "portrait" if folder == "portrait" else "display"
            if source_variant not in variants:
                continue
            for file in directory.glob("*.png"):
                rel = f"{folder}/{file.name}"
                if rel not in current_names:
                    file.unlink(missing_ok=True)
                    log(f"Removed upstream-deleted image: {rel}")

    return {
        "source_commit": commit_sha,
        "synced_at": int(time.time()),
        "files": next_files,
    }


def options() -> dict[str, Any]:
    raw = load_json(OPTIONS_PATH, {})
    return {
        "inky_birds": bool(raw.get("inky_birds", True)),
        "orientation": str(raw.get("orientation", "portrait")),
        "update_interval_hours": max(1, min(168, int(raw.get("update_interval_hours", 24)))),
        "delete_removed": bool(raw.get("delete_removed", True)),
    }


def sync_once() -> bool:
    opts = options()
    orientation = opts["orientation"]
    if orientation not in {"portrait", "landscape", "both"}:
        raise RuntimeError(f"Unsupported orientation: {orientation}")

    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    state = load_json(STATE_PATH, {})
    ok = True

    if opts["inky_birds"]:
        try:
            state["inky_birds"] = sync_collection(
                COLLECTIONS["inky_birds"],
                orientation,
                opts["delete_removed"],
                state,
            )
            write_json(STATE_PATH, state)
        except Exception as error:
            ok = False
            log(f"ERROR: Inky Bird Frame sync failed: {error}")
    else:
        log("Inky Bird Frame is disabled; existing files are left untouched")

    index = {
        "version": 1,
        "updated_at": int(time.time()),
        "orientation": orientation,
        "collections": {
            "birds": {
                "source": "Inky Bird Frame",
                "portrait": str(MEDIA_ROOT / "birds" / "portrait"),
                "landscape": str(MEDIA_ROOT / "birds" / "landscape"),
            }
        },
    }
    write_json(MEDIA_ROOT / "index.json", index)
    return ok


def main() -> int:
    log(f"Starting Nature Frame Sync {APP_VERSION}")
    while True:
        started = time.monotonic()
        sync_once()
        opts = options()
        interval = opts["update_interval_hours"] * 3600
        elapsed = time.monotonic() - started
        sleep_for = max(60, interval - elapsed)
        log(f"Next sync in approximately {sleep_for / 3600:.1f} hour(s)")
        time.sleep(sleep_for)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        log("Stopped")
        raise SystemExit(0)
