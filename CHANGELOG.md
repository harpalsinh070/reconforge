# Changelog

All notable changes to the ReconForge project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-12

### Added
- **Modern CLI Interface:** High-speed Click and Rich-powered command-line interface inspired by Nmap and Nuclei.
- **Robust Debian Packaging:** Production-grade `build_deb.sh` and cross-platform `build_deb.py` generating standard `reconforge_1.0.0_all.deb`.
- **Target Normalization Engine:** Automatic URL, scheme, port, and credential stripping with RFC-compliant validation for domain names and IPv4/IPv6 addresses.
- **Scope & Exclusion Controls:** Granular `--scope` and `--exclude` host/wildcard rules to protect out-of-scope assets.
- **Resilient Passive OSINT:** Certificate Transparency lookup via `crt.sh` and AlienVault OTX integration with rate limit and timeout resilience.
- **Asset Discovery Pipeline:** Asynchronous DNS resolution, wildcard DNS detection and filtering, and Dangling CNAME takeover checks.
- **Service Discovery & Safe Probing:** High-speed async TCP socket scanner with optional Nmap integration and conservative web-security checks.
- **Machine-Readable Automation:** Native `--json` stdout output, `-o` file/directory report saving, `-v` verbose, and `-q` quiet modes.
- **Interactive Shell:** Metasploit-style assessment console (`reconforge console`) with tab completion and live database inspection.
- **Signed APT Repository Setup:** Automation scripts (`scripts/generate_apt_repo.sh` and `.github/workflows/release.yml`) for static, signed APT repository distribution on GitHub Pages.
- **Automated Test Suite:** Comprehensive pytest suite covering target normalization, deduplication, passive OSINT resilience, CLI commands, and Debian package integrity.

### Fixed
- Fixed missing `reconforge/` source tree directory packaging issue in `build_deb.sh`.
- Added missing `greenlet` dependency required by SQLAlchemy asyncio runtime.
- Fixed database record duplication on target rescans.
- Resolved Windows console character encoding in package build output.
