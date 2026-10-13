# Troubleshooting Runbook
1. Confirm the backend health endpoint returns `status: ok`.
2. Enable demo mode to separate UI/API problems from local OS or network restrictions.
3. For DNS failures, verify the hostname and local resolver configuration.
4. For TCP failures, verify port, service availability, firewall, route, and timeout.
5. If SQLite cannot open, verify write permission in the backend working directory and `EDST_DATABASE_URL`.
6. For frontend API errors, confirm `VITE_API_URL` and CORS origin.
Never paste passwords, tokens, cookies, or private file contents into incidents or reports.
