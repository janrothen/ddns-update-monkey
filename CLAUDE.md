# DDNS Update Monkey

A lightweight script that keeps a DuckDNS hostname pointed at your home IP address.
It runs periodically and only calls the DuckDNS API when the public IP has actually changed.

## What it does

1. Fetches the current public IP from `ipv4.icanhazip.com`
2. Compares it to the last known IP (stored in `state.json`)
3. If the IP changed, calls the DuckDNS update API with your token and new IP
4. Logs every action with a timestamp

## Target environment
- Hardware: Raspberry Pi 4, 8 GB RAM
- OS: Debian GNU/Linux 13 (trixie), aarch64
- Python: 3.13.5

## Project structure
```
ddns-update-monkey/
├── src/monkey/
│   ├── __init__.py
│   ├── __main__.py            # Entry point: python -m monkey (composes collaborators)
│   ├── _http.py               # Internal HTTP helper with uniform error wrapping
│   ├── config.py              # Config dataclass + lazy load_config()/env()
│   ├── ip_resolver.py         # IpResolver — fetches the current public IP
│   ├── state_store.py         # StateStore — persists the last known IP atomically
│   ├── duck_dns_client.py     # DuckDnsClient — thin DuckDNS HTTP client
│   └── duck_dns_updater.py    # DuckDnsUpdater — orchestrator
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_duck_dns_client.py
│   ├── test_ip_resolver.py
│   ├── test_main.py
│   ├── test_state_store.py
│   └── test_updater.py
├── .github/workflows/
│   └── sonarcloud.yml        # SonarCloud static analysis CI workflow
├── deploy/cron/
│   ├── ddns-update-monkey    # Cron job — copy to /etc/cron.d/ on the Pi
│   └── README.md             # Installation instructions
├── config.toml               # Non-secret tunables (URLs, timeouts, file paths)
├── pyproject.toml            # Python project metadata and dependencies
├── sonar-project.properties  # SonarCloud project configuration
├── .env                      # Token + domain (never commit this)
├── .env.example              # Safe-to-commit template
├── state.json                # Persisted last known IP (auto-created)
└── CLAUDE.md                 # This file
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:
```env
DUCKDNS_TOKEN=your-token-here
DUCKDNS_DOMAIN=your-subdomain
```

The token is found at the top of the DuckDNS dashboard after logging in.
The domain is just the subdomain part, without `.duckdns.org`.

Non-secret settings (IP service URL, timeouts, file paths) live in `config.toml`.

## Run
```bash
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python -m monkey
```

## Test
```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

## Cron (every 5 minutes)
See `deploy/cron/ddns-update-monkey` — copy it to `/etc/cron.d/` on the Pi.
Logs go to `/var/log/ddns-update-monkey-cron.log`.

## Security notes

- The DuckDNS token grants full control over your domains; treat it like a password
- `.env` is excluded from Git via `.gitignore` — never commit it
