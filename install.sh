#!/usr/bin/env bash
# ReconForge Universal Linux Installation Script
# Supports: Kali Linux, Debian, Ubuntu, Parrot OS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "    ReconForge Linux Installation (CLI & Terminal Tool)   "
echo "=========================================================="

# Check root privileges
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    echo "[-] Error: This installation script requires root privileges." >&2
    echo "[*] Please re-run with sudo: sudo ./install.sh" >&2
    exit 1
fi

# 1. Update and install base runtime dependencies
echo "[+] Installing system prerequisites (Python 3, venv, dnsutils)..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    dnsutils || apt-get install -y --no-install-recommends bind9-dnsutils

# 2. Build Debian package
echo "[+] Compiling Debian package (reconforge_1.0.0_all.deb)..."
bash ./build_deb.sh

# 3. Install Debian package using APT
echo "[+] Installing ReconForge package via APT..."
apt-get install -y ./reconforge_1.0.0_all.deb

# 4. Check external security tool integration
echo ""
echo "[+] Testing ReconForge installation..."
reconforge --check

echo ""
echo "=========================================================="
echo "[+] ReconForge has been successfully installed!"
echo ""
echo "ReconForge can now be executed by ANY user from any terminal:"
echo ""
echo "  1. Quick Discovery:"
echo "     reconforge scan -d example.com --quick"
echo ""
echo "  2. Passive OSINT (No probing):"
echo "     reconforge scan -d example.com --passive"
echo ""
echo "  3. Subdomain Enumeration:"
echo "     reconforge subdomains -d example.com"
echo ""
echo "  4. Interactive Shell:"
echo "     reconforge console"
echo ""
echo "  5. JSON Deliverable for Automation:"
echo "     reconforge scan -d example.com --json > report.json"
echo "=========================================================="
