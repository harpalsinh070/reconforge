#!/usr/bin/env bash
# ReconForge Debian Package Builder
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================"
echo "      Building ReconForge Debian Package (.deb)       "
echo "======================================================"

# Verify source presence
if [ ! -d "reconforge" ]; then
    echo "[-] Error: 'reconforge' source directory not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Ensure debian scripts have executable permissions
chmod 755 debian/DEBIAN/postinst 2>/dev/null || true
chmod 755 debian/DEBIAN/prerm 2>/dev/null || true
chmod 755 debian/DEBIAN/postrm 2>/dev/null || true
chmod 755 debian/usr/bin/reconforge 2>/dev/null || true

# Check if dpkg-deb is available, otherwise use Python builder
if command -v dpkg-deb >/dev/null 2>&1; then
    echo "[+] Native dpkg-deb detected. Staging package files..."
    rm -rf build_staging
    mkdir -p build_staging/usr/share/reconforge
    mkdir -p build_staging/usr/bin
    mkdir -p build_staging/usr/share/doc/reconforge
    mkdir -p build_staging/DEBIAN

    # Copy files
    cp -r reconforge build_staging/usr/share/reconforge/
    cp requirements.txt setup.py pyproject.toml README.md LICENSE build_staging/usr/share/reconforge/
    cp debian/usr/bin/reconforge build_staging/usr/bin/reconforge
    cp debian/DEBIAN/* build_staging/DEBIAN/
    cp README.md build_staging/usr/share/doc/reconforge/README
    cp LICENSE build_staging/usr/share/doc/reconforge/copyright

    # Clean any pycache in staging
    find build_staging -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find build_staging -type f -name "*.pyc" -delete 2>/dev/null || true

    # Compute md5sums
    cd build_staging
    find usr -type f -exec md5sum {} + > DEBIAN/md5sums
    cd ..

    # Set permissions
    chmod 755 build_staging/DEBIAN/postinst
    chmod 755 build_staging/DEBIAN/prerm
    chmod 755 build_staging/DEBIAN/postrm
    chmod 755 build_staging/usr/bin/reconforge

    echo "[+] Packing reconforge_1.0.0_all.deb using dpkg-deb..."
    dpkg-deb --build --root-owner-group build_staging reconforge_1.0.0_all.deb
    rm -rf build_staging
else
    echo "[*] dpkg-deb not found in PATH. Using built-in Python Debian package generator..."
    python3 build_deb.py
fi

echo ""
echo "======================================================"
echo "[+] Build successful: reconforge_1.0.0_all.deb"
echo ""
echo "To install via APT on Debian / Ubuntu / Kali Linux:"
echo "    sudo apt install ./reconforge_1.0.0_all.deb"
echo ""
echo "Or using dpkg directly:"
echo "    sudo dpkg -i reconforge_1.0.0_all.deb"
echo "    sudo apt-get install -f"
echo "======================================================"
