# Security Policy & Responsible Use Guidelines

## 1. Responsible Use & Authorization

ReconForge is designed exclusively for authorized cybersecurity assessments, penetration testing, security auditing, and defensive asset management.

- **Mandatory Authorization:** You must have explicit, documented authorization from the target asset's owner before initiating any active reconnaissance, port discovery, or web endpoint probing.
- **Compliance:** Ensure all activities comply with applicable local, national, and international laws, including computer fraud and abuse legislation.
- **Scope Discipline:** Always enforce explicit scope constraints (`--scope`) and exclude restricted internal systems or third-party gateways (`--exclude`).

## 2. Safe Operational Guarantees

ReconForge is engineered to be conservative and defensive:
- **No Exploitation:** ReconForge does not generate functional attack exploits, destructive payloads, or automated attack scripts.
- **No Weaponized Probes:** Exposure detection tests verify publicly accessible metadata and HTTP status codes without modifying server-side state.
- **Banner Integrity:** Service versions and banners are cataloged objectively without asserting confirmed vulnerabilities solely from banner strings.

## 3. Reporting Vulnerabilities in ReconForge

If you discover a security vulnerability within the ReconForge codebase itself:
1. Do not open public GitHub issues for undisclosed security flaws.
2. Submit a responsible disclosure report via email to `security@reconforge.local`.
3. Include clear steps to reproduce, affected versions, and proposed remediations.
4. The maintenance team will acknowledge receipt within 48 hours and work with you to prepare a patch prior to public release.
