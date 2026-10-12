#!/usr/bin/env python3
"""
ReconForge Standalone Debian Package (.deb) Builder
Builds compliant Debian archives with standard Unix ar and tar.gz payloads.
Supports cross-platform building on Linux, macOS, and Windows.
"""

import os
import sys
import io
import time
import shutil
import hashlib
import tarfile
from pathlib import Path

PACKAGE_NAME = "reconforge"
VERSION = "1.0.0"
ARCHITECTURE = "all"
DEB_FILENAME = f"{PACKAGE_NAME}_{VERSION}_{ARCHITECTURE}.deb"

def compute_md5(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def make_ar_header(name: str, size: int, mode: int = 0o100644, mtime: int = 0, uid: int = 0, gid: int = 0) -> bytes:
    """Format a 60-byte standard Unix ar header."""
    # Ensure name ends with '/' according to System V / Debian ar format
    ar_name = (name + "/").ljust(16)
    ar_mtime = str(int(mtime)).ljust(12)
    ar_uid = str(uid).ljust(6)
    ar_gid = str(gid).ljust(6)
    ar_mode = oct(mode)[2:].ljust(8)
    ar_size = str(size).ljust(10)
    trailer = b"`\n"

    header = (
        ar_name.encode("ascii") +
        ar_mtime.encode("ascii") +
        ar_uid.encode("ascii") +
        ar_gid.encode("ascii") +
        ar_mode.encode("ascii") +
        ar_size.encode("ascii") +
        trailer
    )
    if len(header) != 60:
        raise ValueError(f"Invalid ar header size: {len(header)}")
    return header

def stage_package(root_dir: Path, staging_dir: Path):
    """Stage project files into Debian filesystem hierarchy."""
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    debian_dir = root_dir / "debian"
    src_dir = root_dir / "reconforge"

    if not src_dir.exists():
        raise FileNotFoundError(f"Missing core source directory: {src_dir}")

    # Create directories
    share_dir = staging_dir / "usr" / "share" / "reconforge"
    bin_dir = staging_dir / "usr" / "bin"
    doc_dir = staging_dir / "usr" / "share" / "doc" / "reconforge"
    control_dir = staging_dir / "DEBIAN"

    for d in [share_dir, bin_dir, doc_dir, control_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Copy source code (ignoring caches)
    def ignore_pycache(dir, files):
        return [f for f in files if f == "__pycache__" or f.endswith(".pyc") or f == ".pytest_cache"]

    shutil.copytree(src_dir, share_dir / "reconforge", ignore=ignore_pycache)

    # 2. Copy metadata files
    for item in ["requirements.txt", "setup.py", "pyproject.toml", "README.md", "LICENSE"]:
        src_file = root_dir / item
        if src_file.exists():
            shutil.copy2(src_file, share_dir / item)

    # 3. Copy launcher
    launcher_src = debian_dir / "usr" / "bin" / "reconforge"
    if launcher_src.exists():
        shutil.copy2(launcher_src, bin_dir / "reconforge")
    else:
        # Fallback launcher
        launcher_content = """#!/usr/bin/env bash
if [ -x "/usr/share/reconforge/venv/bin/reconforge" ]; then
    exec "/usr/share/reconforge/venv/bin/reconforge" "$@"
elif [ -x "/usr/share/reconforge/venv/bin/python3" ]; then
    export PYTHONPATH="/usr/share/reconforge:$PYTHONPATH"
    exec "/usr/share/reconforge/venv/bin/python3" -m reconforge "$@"
else
    exec python3 -m reconforge "$@"
fi
"""
        with open(bin_dir / "reconforge", "w", newline="\n", encoding="utf-8") as f:
            f.write(launcher_content)

    # 4. Copy docs
    if (root_dir / "README.md").exists():
        shutil.copy2(root_dir / "README.md", doc_dir / "README")
    if (root_dir / "LICENSE").exists():
        shutil.copy2(root_dir / "LICENSE", doc_dir / "copyright")

    # 5. Copy DEBIAN control scripts
    for script in ["control", "postinst", "prerm", "postrm"]:
        s_src = debian_dir / "DEBIAN" / script
        if s_src.exists():
            shutil.copy2(s_src, control_dir / script)

    # 6. Generate md5sums for files under usr/
    md5_lines = []
    usr_dir = staging_dir / "usr"
    for p in sorted(usr_dir.rglob("*")):
        if p.is_file():
            rel_path = p.relative_to(staging_dir).as_posix()
            md5_val = compute_md5(p)
            md5_lines.append(f"{md5_val}  {rel_path}\n")

    with open(control_dir / "md5sums", "w", newline="\n", encoding="utf-8") as f:
        f.writelines(md5_lines)

def build_tar_gz(base_dir: Path, archive_type: str) -> bytes:
    """Build a deterministic tar.gz archive for DEBIAN control or data."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as tar:
        for root, dirs, files in os.walk(base_dir):
            dirs.sort()
            files.sort()
            
            # If packing data, exclude the DEBIAN metadata directory
            if archive_type == "data":
                if "DEBIAN" in dirs:
                    dirs.remove("DEBIAN")
                if Path(root).name == "DEBIAN" or "DEBIAN" in Path(root).parts:
                    continue

            rel_root = Path(root).relative_to(base_dir)
            
            if rel_root != Path("."):
                dir_path = ("./" + rel_root.as_posix()) if archive_type == "data" else rel_root.as_posix()
                ti = tar.gettarinfo(root, arcname=dir_path)
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                ti.mode = 0o755
                ti.mtime = 1700000000
                tar.addfile(ti)

            for file_name in files:
                file_path = Path(root) / file_name
                rel_file = file_path.relative_to(base_dir)
                arc_name = ("./" + rel_file.as_posix()) if archive_type == "data" else rel_file.as_posix()
                
                ti = tar.gettarinfo(str(file_path), arcname=arc_name)
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                ti.mtime = 1700000000

                # Determine executable mode
                if file_name in ["postinst", "prerm", "postrm"] or file_name == "reconforge" or file_name.endswith(".sh"):
                    ti.mode = 0o755
                else:
                    ti.mode = 0o644

                with open(file_path, "rb") as f:
                    tar.addfile(ti, f)

    return buf.getvalue()

def build_deb_package(root_dir: Path, output_file: Path):
    """Assemble final .deb package using standard ar format."""
    staging_dir = root_dir / "build_staging"
    stage_package(root_dir, staging_dir)

    print(f"[+] Packing control.tar.gz...")
    control_data = build_tar_gz(staging_dir / "DEBIAN", "control")

    print(f"[+] Packing data.tar.gz...")
    data_data = build_tar_gz(staging_dir, "data")

    debian_binary = b"2.0\n"

    print(f"[+] Writing Debian archive: {output_file.name}...")
    with open(output_file, "wb") as deb:
        # 1. Global ar magic
        deb.write(b"!<arch>\n")

        # 2. Member: debian-binary
        deb.write(make_ar_header("debian-binary", len(debian_binary), mode=0o100644))
        deb.write(debian_binary)

        # 3. Member: control.tar.gz
        deb.write(make_ar_header("control.tar.gz", len(control_data), mode=0o100644))
        deb.write(control_data)
        if len(control_data) % 2 != 0:
            deb.write(b"\n")

        # 4. Member: data.tar.gz
        deb.write(make_ar_header("data.tar.gz", len(data_data), mode=0o100644))
        deb.write(data_data)
        if len(data_data) % 2 != 0:
            deb.write(b"\n")

    pkg_size = output_file.stat().st_size
    print(f"[OK] Package built successfully: {output_file} ({pkg_size:,} bytes)")
    return output_file

def main():
    root = Path(__file__).resolve().parent
    out = root / DEB_FILENAME
    print("======================================================")
    print("      Building ReconForge Debian Package (.deb)       ")
    print("======================================================")
    build_deb_package(root, out)

if __name__ == "__main__":
    main()
