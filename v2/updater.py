"""ACE Adventures 2 staged updater core. Does not modify a .app bundle.
All URLs must be trusted, all file hashes checked, and activation atomic.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import ssl
import certifi
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ALLOWED_HOST = "raw.githubusercontent.com"
ALLOWED_PREFIX = "/LGBerlin/ACE-Adventures/main/v2/updates/"

def version(v: str) -> tuple[int, int, int]:
    pieces = v.split(".")
    if len(pieces) != 3 or any(not p.isdecimal() for p in pieces):
        raise ValueError("Invalid version")
    return tuple(map(int, pieces))

def safe_path(p: str) -> Path:
    x = Path(p)
    if x.is_absolute() or not p or any(part in (".", "..") for part in x.parts) or "\\" in p:
        raise ValueError("Unsafe update path")
    return x

def validate_manifest(m: dict, installed: str) -> list[dict]:
    target = version(m["version"])
    if target <= version(installed):
        raise ValueError("Not a newer version")
    if m.get("base") != installed:
        raise ValueError("Patch base does not match installed version")
    items = m["files"]
    if not isinstance(items, list) or not items or len(items) > 500:
        raise ValueError("Invalid update file list")
    names = set()
    for f in items:
        name = str(safe_path(f["path"]))
        if name in names:
            raise ValueError("Duplicate file path")
        names.add(name)
        digest = f["sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid checksum")
        parsed = urlsplit(f["url"])
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST or not parsed.path.startswith(ALLOWED_PREFIX):
            raise ValueError("Untrusted download URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Unexpected URL decoration")
    return items

def load_active(root: Path) -> dict:
    marker = root / "active.json"
    if not marker.exists():
        return {"version": "0.0.0", "directory": None}
    return json.loads(marker.read_text(encoding="utf-8"))

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def activate(root: Path, manifest: dict, fetch=None) -> Path:
    """Stage and verify before an atomic pointer update. Raise on any failure."""
    root.mkdir(parents=True, exist_ok=True)
    active = load_active(root)
    items = validate_manifest(manifest, active["version"])
    fetch = fetch or _fetch
    release = root / "versions" / manifest["version"]
    if release.exists():
        raise ValueError("Version directory already exists")
    staging_parent = root / "staging"
    staging_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=staging_parent) as temp:
        stage = Path(temp)
        previous = active.get("directory")
        if previous:
            source = (root / "versions" / previous).resolve()
            versions = (root / "versions").resolve()
            if source.parent != versions or not source.is_dir():
                raise ValueError("Missing active payload")
            shutil.copytree(source, stage, dirs_exist_ok=True)
        for item in items:
            body = fetch(item["url"])
            if not isinstance(body, bytes) or len(body) > 25_000_000:
                raise ValueError("Invalid or oversized file")
            if sha256(body) != item["sha256"]:
                raise ValueError("Checksum mismatch")
            out = stage / safe_path(item["path"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(body)
        release.parent.mkdir(exist_ok=True)
        os.replace(stage, release)
    new_pointer = {"version": manifest["version"], "directory": manifest["version"], "previous": active.get("directory")}
    marker_tmp = root / "active.json.new"
    marker_tmp.write_text(json.dumps(new_pointer, indent=2), encoding="utf-8")
    os.replace(marker_tmp, root / "active.json")
    return release

def rollback(root: Path) -> None:
    active = load_active(root)
    previous = active.get("previous")
    if not previous or not (root / "versions" / previous).is_dir():
        raise ValueError("No rollback version")
    marker_tmp = root / "active.json.new"
    marker_tmp.write_text(json.dumps({"version": previous, "directory": previous, "previous": active["directory"]}), encoding="utf-8")
    os.replace(marker_tmp, root / "active.json")

def _fetch(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "ACE-Adventures-2"}), timeout=25, context=ssl.create_default_context(cafile=certifi.where())) as response:
        return response.read(25_000_001)
