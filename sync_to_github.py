#!/usr/bin/env python3
"""
ReconForge GitHub Direct Repository Synchronizer
Pushes the entire project tree directly to https://github.com/harpalsinh070/reconxforge
using GitHub REST / Git Data APIs without requiring local git installation.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path

REPO_OWNER = "harpalsinh070"
REPO_NAME = "reconxforge"
BRANCH = "main"

EXCLUDE_DIRS = {".venv", "__pycache__", ".pytest_cache", ".git", "build_staging"}
EXCLUDE_EXTENSIONS = {".pyc"}

def github_request(endpoint: str, token: str, data: dict = None, method: str = None) -> dict:
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ReconForge-Sync"
    }

    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            return json.loads(content.decode("utf-8")) if content else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API Error [{e.code}]: {err_msg}")

def get_latest_commit_sha(token: str) -> str:
    try:
        ref_data = github_request(f"git/ref/heads/{BRANCH}", token)
        return ref_data["object"]["sha"]
    except Exception:
        # Branch might not exist or be empty
        return None

def upload_file_blob(file_path: Path, token: str) -> str:
    with open(file_path, "rb") as f:
        content_bytes = f.read()
    b64_content = base64.b64encode(content_bytes).decode("ascii")
    blob_data = github_request("git/blobs", token, {
        "content": b64_content,
        "encoding": "base64"
    }, method="POST")
    return blob_data["sha"]

def sync_repository(token: str):
    root_dir = Path(__file__).resolve().parent
    print(f"[*] Starting ReconForge sync to {REPO_OWNER}/{REPO_NAME} ({BRANCH})...")

    # 1. Discover all project files
    files_to_upload = []
    for path in root_dir.rglob("*"):
        if path.is_file():
            # Check exclusions
            parts = set(path.parts)
            if any(ex in parts for ex in EXCLUDE_DIRS):
                continue
            if path.suffix in EXCLUDE_EXTENSIONS:
                continue
            if path.name == "sync_to_github.py":
                continue
            rel_path = path.relative_to(root_dir).as_posix()
            files_to_upload.append((path, rel_path))

    print(f"[+] Found {len(files_to_upload)} files to synchronize.")

    # 2. Upload blobs and construct git tree items
    tree_items = []
    for idx, (fpath, rel_path) in enumerate(files_to_upload, start=1):
        print(f"    [{idx}/{len(files_to_upload)}] Uploading blob: {rel_path}...")
        sha = upload_file_blob(fpath, token)
        # Set executable mode 100755 for scripts and binaries
        is_executable = (
            rel_path.endswith(".sh") or
            rel_path.endswith("/reconforge") or
            rel_path == "build_deb.sh"
        )
        mode = "100755" if is_executable else "100644"
        tree_items.append({
            "path": rel_path,
            "mode": mode,
            "type": "blob",
            "sha": sha
        })

    # 3. Create Git Tree
    print("[*] Creating remote Git Tree...")
    tree_data = github_request("git/trees", token, {"tree": tree_items}, method="POST")
    tree_sha = tree_data["sha"]

    # 4. Create Commit
    latest_commit_sha = get_latest_commit_sha(token)
    commit_payload = {
        "message": "Refactor ReconForge: complete source package, modular scan pipeline, and Debian build scripts",
        "tree": tree_sha,
        "parents": [latest_commit_sha] if latest_commit_sha else []
    }
    print("[*] Creating commit...")
    commit_data = github_request("git/commits", token, commit_payload, method="POST")
    new_commit_sha = commit_data["sha"]

    # 5. Update branch pointer
    print(f"[*] Updating {BRANCH} branch pointer...")
    if latest_commit_sha:
        github_request(f"git/refs/heads/{BRANCH}", token, {
            "sha": new_commit_sha,
            "force": True
        }, method="PATCH")
    else:
        github_request("git/refs", token, {
            "ref": f"refs/heads/{BRANCH}",
            "sha": new_commit_sha
        }, method="POST")

    print("")
    print("==============================================================")
    print(f"[SUCCESS] All files successfully pushed to https://github.com/{REPO_OWNER}/{REPO_NAME}!")
    print(f"Commit SHA: {new_commit_sha}")
    print("You can now run 'git pull' or a fresh 'git clone' on Kali Linux.")
    print("==============================================================")

if __name__ == "__main__":
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    elif "GITHUB_TOKEN" in os.environ:
        token = os.environ["GITHUB_TOKEN"].strip()
    else:
        token = input("Enter your GitHub Personal Access Token (PAT): ").strip()

    if not token:
        print("[-] Error: GitHub token is required.")
        sys.exit(1)

    sync_repository(token)
