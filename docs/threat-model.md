# Threat Model
## Assets
Diagnostic summaries, incident text, local hostname, SQLite history.
## Trust boundaries
Browser to localhost API; API to OS/network libraries; API to SQLite.
## Controls
- No shell execution or arbitrary commands.
- Hostname and port validation; short network timeouts.
- HTTP URL checker omitted, removing its SSRF surface.
- Data minimization: no passwords, tokens, cookies, browser history, file contents, MAC addresses, or serial numbers.
- Predictable errors without stack traces; request IDs for correlation.
- Local-only default and explicit report-sharing warning.
## Residual risks
Incident notes may contain user-entered sensitive data. Operators must follow the warning and review reports before sharing.
