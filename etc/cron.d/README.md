# Automated Scheduling with Cron

The project includes a cron file (`etc/cron.d/ddns-update-monkey`) that runs the DDNS updater every 5 minutes.

## Installation steps

### 1. Copy the scheduling file
```bash
sudo cp etc/cron.d/ddns-update-monkey /etc/cron.d/
```

### 2. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/ddns-update-monkey
sudo chown root:root /etc/cron.d/ddns-update-monkey
```

### 3. Create the log file
The cron job runs as user `pi` which cannot create files in `/var/log/` by default:
```bash
sudo touch /var/log/ddns-update-monkey-cron.log
sudo chown pi:pi /var/log/ddns-update-monkey-cron.log
```

### 4. Verify cron picked it up
```bash
sudo systemctl status cron
```

## Logs

Output is appended to `/var/log/ddns-update-monkey-cron.log`:
```bash
tail -f /var/log/ddns-update-monkey-cron.log
```
