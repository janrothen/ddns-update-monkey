# DDNS Update Monkey

Keeps a [DuckDNS](https://www.duckdns.org) hostname pointed at your home IP.
Runs periodically and only calls the DuckDNS API when the IP actually changes.

## How it works

1. Fetches your current public IP from `ipv4.icanhazip.com`
2. Compares it to the last known IP (persisted in `state.json`)
3. If it changed, calls the DuckDNS update API
4. Logs every action with a timestamp to stdout

## Requirements

- Python 3.13+
- A free [DuckDNS](https://www.duckdns.org) account with a domain set up

## Configuration

Configuration is split across two files intentionally:

- **`.env`** — secrets (credentials). Never commit this file.
- **`config.toml`** — non-secret settings (IP, timeouts, file paths).

### Credentials (`.env`)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```dotenv
DUCKDNS_TOKEN=your-token-here
DUCKDNS_DOMAIN=your-subdomain
```

The token is at the top of the DuckDNS dashboard. The domain is just the subdomain part, without `.duckdns.org`.


### Settings (`config.toml`)

```toml
[ip]
service_url     = "https://ipv4.icanhazip.com"
request_timeout = 10

[duckdns]
update_url      = "https://www.duckdns.org/update"
request_timeout = 10

[files]
state = "state.json"
```

## Install & run

```bash
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python -m monkey
```


## Run as a cron job  (every 5 minutes)

If you cloned the repo somewhere other than `/home/pi/ddns-update-monkey/`, update the `HOME` variable at the top of `etc/cron.d/ddnsupdatemonkey` first. Then:

```bash
# Install the cron file
sudo cp etc/cron.d/ddnsupdatemonkey /etc/cron.d/
sudo chmod 644 /etc/cron.d/ddnsupdatemonkey
sudo chown root:root /etc/cron.d/ddnsupdatemonkey

# Create the log file (cron runs as user pi)
sudo touch /var/log/ddnsupdatemonkey-cron.log
sudo chown pi:pi /var/log/ddnsupdatemonkey-cron.log

# Verify cron picked it up
sudo systemctl status cron
```

To follow logs:
```bash
tail -f /var/log/ddnsupdatemonkey-cron.log
```

## Development & testing

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Missing required environment variable: DUCKDNS_TOKEN` | `.env` is missing or the variable name is wrong |
| `IP service returned HTTP 4xx/5xx` | `ipv4.icanhazip.com` is temporarily unavailable — will retry on next cron tick |
| `DuckDNS returned HTTP 4xx` | Token is invalid or expired — check the DuckDNS dashboard |
| `DuckDNS returned unexpected response` | DuckDNS API returned something other than `OK` — check the domain name |
| `state.json is corrupt` | State file was partially written — it is reset automatically |

## Security

- `.env` is listed in `.gitignore` and must never be committed — it contains your DuckDNS token
- The token grants full control over your DuckDNS domains; treat it like a password


## State file

`state.json` persists the IP from the previous run. On first run the file doesn't exist yet, so the IP is treated as unknown and DuckDNS is updated immediately. If the file is deleted, the same bootstrap happens on the next run.