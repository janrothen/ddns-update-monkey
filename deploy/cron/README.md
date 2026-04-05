# Automated Scheduling with Cron

The project includes a cron file (`ddns-update-monkey`) that runs the DDNS updater every 5 minutes.

## Installation steps

### 1. Set the repo path

Update the `HOME` variable at the top of `bitcoin-node-watchdog` to match where you cloned the repo.

### 2. Copy the scheduling file
```bash
sudo cp ddns-update-monkey /etc/cron.d/
```

### 3. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/ddns-update-monkey
sudo chown root:root /etc/cron.d/ddns-update-monkey
```

### 4. Create the log file
The cron job runs as user `pi` which cannot create files in `/var/log/` by default:
```bash
sudo touch /var/log/ddns-update-monkey-cron.log
sudo chown pi:pi /var/log/ddns-update-monkey-cron.log
```

### 5. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Logs

Output is appended to `/var/log/ddns-update-monkey-cron.log`:
```bash
tail -f /var/log/ddns-update-monkey-cron.log
```
