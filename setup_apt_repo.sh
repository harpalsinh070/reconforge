#!/usr/bin/env bash
# ReconForge Local APT Repository Setup Script
# Configures a local filesystem repository for testing apt update & apt install reconforge
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo "[-] Error: This script requires root privileges (sudo ./setup_apt_repo.sh)" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "    Setting up Local APT Repository for ReconForge        "
echo "=========================================================="

# 1. Build deb package if missing
if [ ! -f "reconforge_1.0.0_all.deb" ]; then
    echo "[+] Building Debian package..."
    bash ./build_deb.sh
fi

REPO_DIR="/var/local/reconforge-repo"
echo "[+] Preparing local repository directory: $REPO_DIR..."
mkdir -p "$REPO_DIR"
cp reconforge_1.0.0_all.deb "$REPO_DIR/"

# 2. Check for dpkg-scanpackages (part of dpkg-dev)
if ! command -v dpkg-scanpackages &> /dev/null; then
    echo "[+] Installing dpkg-dev for local repository indexing..."
    apt-get update -qq && apt-get install -y -qq dpkg-dev
fi

# 3. Index repository
echo "[+] Generating Packages index..."
(
    cd "$REPO_DIR"
    dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz
)

# 4. Configure APT source entry
SOURCE_FILE="/etc/apt/sources.list.d/reconforge-local.list"
echo "deb [trusted=yes] file:$REPO_DIR ./" > "$SOURCE_FILE"

echo "[+] Updating APT cache..."
apt-get update -qq

echo ""
echo "=========================================================="
echo "[+] Local APT repository configured successfully!"
echo "You can now install or upgrade ReconForge via native APT:"
echo ""
echo "    sudo apt install reconforge"
echo ""
echo "=========================================================="
