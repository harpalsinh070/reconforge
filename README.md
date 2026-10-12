# ReconForge - Linux Terminal Reconnaissance & Attack Surface Management Platform

[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali%20%7C%20Debian%20%7C%20Ubuntu-blue.svg)](#)
[![Package](https://img.shields.io/badge/package-apt%20%7C%20dpkg%20(.deb)-emerald.svg)](#)
[![Python](https://img.shields.io/badge/python-3.9%2B-cyan.svg)](#)
[![Interface](https://img.shields.io/badge/interface-CLI%20(nmap--style)%20%2B%20Console%20(msfconsole--style)-purple.svg)](#)
[![License](https://img.shields.io/badge/license-GPL--3.0-red.svg)](#)

> **ReconForge** is a production-grade, terminal-native reconnaissance and attack surface discovery tool engineered for **authorized security assessments, penetration testing, and defensive asset inventory** on Debian, Ubuntu, and Kali Linux.

Designed as an installable CLI utility inspired by the speed and usability of **Nmap** and **Nuclei**, ReconForge provides:
1. **Nmap-Style Direct Execution:** Fast CLI commands (`reconforge scan -d example.com`, `reconforge subdomains -d example.com`).
2. **Interactive Assessment Console:** Metasploit-style shell with persistent state and tab autocompletion (`reconforge console`).
3. **Modular Reconnaissance Pipeline:** 10-phase pipeline separating target validation, passive OSINT, DNS resolution, IP mapping, port discovery, HTTP fingerprinting, security auditing, and correlated reporting.
4. **Debian & APT Package Distribution:** Native `.deb` package packaging with support for signed APT repositories.
5. **Machine-Readable Automation:** Native `--json` output, configurable verbosity (`-v`, `-q`), and plain-text fallback (`--no-color`).

---

```
  ____                      _____                     
 |  _ \ ___  ___ ___  _ __ |  ___|__  _ __ __ _  ___  
 | |_) / _ \/ __/ _ \| '_ \| |_ / _ \| '__/ _` |/ _ \ 
 |  _ <  __/ (_| (_) | | | |  _| (_) | | | (_| |  __/ 
 |_| \_\___|\___\___/|_| |_|_|  \___/|_|  \__, |\___| 
                                          |___/       
  Linux Reconnaissance & Attack Surface Management Tool  |  v1.0.0
```

---

## 1. Quick Start Commands

After installation, the following commands work out-of-the-box:

```bash
# Display help menu and command options
reconforge --help

# Display version information
reconforge --version

# Verify external tooling readiness (Nmap, Subfinder, Nuclei)
reconforge --check

# Standard full reconnaissance scan
reconforge scan -d example.com

# Passive OSINT reconnaissance (zero direct traffic to target hosts)
reconforge scan -d example.com --passive

# High-speed quick triage scan (top 20 network ports)
reconforge scan -d example.com --quick

# Discover and list subdomains for a target
reconforge subdomains -d example.com

# Launch interactive assessment console
reconforge console
```

---

## 2. Installation on Debian, Ubuntu & Kali Linux

### Method A: Local Debian Package (.deb) Build & Install (Recommended)

Clone the repository and build the Debian package using the builder script:

```bash
git clone https://github.com/reconforge/reconforge.git
cd reconforge

# 1. Compile the Debian package (.deb)
bash ./build_deb.sh

# 2. Install the generated package via APT
sudo apt install ./reconforge_1.0.0_all.deb

# 3. Verify installation
reconforge --check
```

To uninstall or remove the package cleanly:
```bash
sudo apt remove reconforge
# Or to purge all residual database and configuration files:
sudo apt purge reconforge
```

---

### Method B: Signed GitHub-Hosted APT Repository

For centralized deployment across fleets or CI/CD runners, configure the signed APT repository:

```bash
# 1. Download and install repository signing key into system keyrings
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://<YOUR_GITHUB_USERNAME>.github.io/reconforge/reconforge.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/reconforge-archive-keyring.gpg

# 2. Add authenticated repository source entry
echo "deb [signed-by=/etc/apt/keyrings/reconforge-archive-keyring.gpg] https://<YOUR_GITHUB_USERNAME>.github.io/reconforge stable main" | sudo tee /etc/apt/sources.list.d/reconforge.list

# 3. Update database and install native package
sudo apt update
sudo apt install reconforge
```

> **Note:** The remote APT repository commands become active once you publish your repository build using the provided GitHub Actions workflow.

---

### Method C: Automated All-in-One Local Installer

For automated local setup:
```bash
sudo bash ./install.sh
```

---

### Method D: Python Development / Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
reconforge --help
```

---

## 3. CLI Options & Command Reference

### `reconforge scan`
Execute full or selective pipeline assessments:

```bash
# Comprehensive assessment with JSON report saved to directory
reconforge scan -d example.com -o ./reports/

# Passive OSINT only (queries crt.sh & AlienVault OTX)
reconforge scan -d example.com --passive

# Quick triage (top ports, active HTTP check)
reconforge scan -d example.com --quick

# Target custom ports
reconforge scan -d example.com -p 80,443,8080,8443,9000

# Explicit scope and exclusions
reconforge scan -d example.com --scope "*.example.com" --exclude "admin.example.com,*.corp.example.com"

# Enable native Nmap engine (when installed in system PATH)
reconforge scan -d example.com --nmap

# Machine-readable JSON output to stdout (ideal for piping to jq)
reconforge scan -d example.com --passive --json

# Plain-text mode (disables ANSI color formatting)
reconforge scan -d example.com --no-color
```

### `reconforge subdomains`
Subdomain enumeration and takeover checking:

```bash
reconforge subdomains -d example.com
reconforge subdomains -d example.com --refresh
reconforge subdomains -d example.com -o subdomains.txt
```

### `reconforge hosts`, `services`, `vulns`
Query offline assessment state stored in `~/.reconforge/reconforge.db`:

```bash
# List all previously scanned targets and risk scores
reconforge hosts

# List open ports and services for a target
reconforge services -d example.com

# List identified findings, missing headers, and exposures
reconforge vulns -d example.com
```

---

## 4. Reconnaissance Pipeline Architecture

ReconForge organizes asset discovery into 10 modular phases:

```
[Phase 1: Target Normalization]
  └─ Strips URL schemes, ports, credentials, and paths; validates RFC-compliant syntax & IP addresses.
[Phase 2: Passive OSINT Reconnaissance]
  └─ Certificate Transparency (crt.sh) & AlienVault OTX lookups without direct probing.
[Phase 3: Active Subdomain Resolution & Wildcards]
  └─ Async DNS resolution; detects and filters wildcard DNS false positives.
[Phase 4: DNS Enumeration & Dangling CNAMEs]
  └─ Collects A, AAAA, MX, NS, TXT; identifies unclaimed dangling CNAME records.
[Phase 5: IP Intelligence & Cloud/ASN Mapping]
  └─ Reverse PTR queries, BGP origin ASN lookups, and cloud/CDN provider identification.
[Phase 6: Port & Service Discovery]
  └─ Async TCP socket engine or optional Nmap integration; safe banner collection.
[Phase 7: HTTP Probing & Tech Fingerprinting]
  └─ HTTP/HTTPS status, titles, headers, WAF signatures (Cloudflare, AWS, Akamai), and CMS stacks.
[Phase 8: TLS Certificate & Security Headers]
  └─ Certificate expiration audit, OWASP recommended headers (HSTS, CSP, X-Frame-Options).
[Phase 9: Safe Exposure & Misconfiguration Audit]
  └─ Safe non-destructive GET requests: .git/HEAD, .env leaks, actuator endpoints, robots.txt.
[Phase 10: Correlation & Deliverables]
  └─ Calculates 0-100 risk score, saves to local SQLite database, and exports structured JSON.
```

---

## 5. Security & Ethical Boundaries

- **Authorization Required:** ReconForge must only be used against targets you own or have explicit written authorization to test.
- **Non-Destructive Checks:** ReconForge does not generate functional exploit scripts, brute-force credentials, or disrupt target availability.
- **Conservative Reporting:** Service banners and versions are cataloged as factual indicators; vulnerabilities are never confirmed solely on banner version strings without verified indicators.

See [SECURITY.md](SECURITY.md) for full policy details.

---

## 6. License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.
