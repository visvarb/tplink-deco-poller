# TPLink Deco Poller for AdGuard

**Automatically generate hosts entries from TPLink Deco router for AdGuard Home**

This script connects to your TPLink Deco router, retrieves all connected devices, and generates a hosts file with proper DNS entries that AdGuard Home can use for local device resolution.

## ✨ Features

- 🚀 **One-command installation** - Download and run a single script
- 🔄 **Automatic updates** - Always downloads the latest version from GitHub
- 🐍 **Virtual environment** - Isolated Python dependencies
- ⏰ **Scheduled execution** - Runs automatically every hour via cron
- 🔒 **Secure configuration** - Password protection with proper file permissions
- 📝 **Comprehensive logging** - Detailed logs with rotation
- 🛡️ **Idempotent setup** - Safe to run multiple times
- 🎯 **Interactive configuration** - Guided setup process

## 📋 Prerequisites

- **Linux server** (Debian/Ubuntu preferred) with AdGuard Home installed
- **Root or sudo access**
- **Internet connection** for downloading dependencies
- **TPLink Deco router** with admin access
- **Python 3.11+** (will be installed automatically if missing)

## 🚀 Quick Installation

**Just download and run the bootstrap script:**

### Option 1: Using wget
```bash
wget https://raw.githubusercontent.com/your-username/tplink-deco-poller/main/bootstrap.py
sudo python3 bootstrap.py
```

### Option 2: Using curl
```bash
curl -O https://raw.githubusercontent.com/your-username/tplink-deco-poller/main/bootstrap.py
sudo python3 bootstrap.py
```

**That's it!** The script will automatically:
- ✅ Check system requirements
- ✅ Install missing dependencies 
- ✅ Download all required files from GitHub
- ✅ Create Python virtual environment
- ✅ Install Python packages from requirements.txt
- ✅ Set up directory structure at `/srv/tplink-deco/`
- ✅ Configure proper file permissions
- ✅ Create cron job for hourly execution
- ✅ Guide you through router credential setup
- ✅ Optionally run the first hosts generation

## ⚙️ Configuration

After installation, configure your router credentials:

```bash
sudo nano /srv/tplink-deco/tplink.env
```

Update with your actual values:
```bash
# Router gateway IP address (e.g., 192.168.1.1 or 10.1.0.1)
TPLINK_GATEWAY=192.168.1.1

# Router admin password
TPLINK_PASSWORD=your_actual_password

# Optional: Enable testing mode (1 for testing, 0 for production)
# TESTING=0
```

## 🧪 Testing

```bash
# Run manually to test
sudo /srv/tplink-deco/run_generate_hosts.sh

# Check the logs
tail -f /srv/tplink-deco/log/output.log

# Verify the hosts file was updated
cat /etc/hosts
```

## 📁 File Structure

After installation, you'll have:
```
/srv/tplink-deco/
├── venv/                    # Python virtual environment
├── log/                     # Log files
│   └── output.log          # Script execution logs
├── generate_hosts.py        # Main script
├── run_generate_hosts.sh    # Runner script with logging
├── requirements.txt         # Python dependencies
└── tplink.env              # Configuration file (secure)
```

## 🔄 Automation

**The script runs automatically every hour** via cron job:
```bash
# View current cron jobs
crontab -l

# Check cron execution logs
grep CRON /var/log/syslog | grep tplink-deco
```

## 🛠️ Manual Operations

```bash
# Run the script immediately
sudo /srv/tplink-deco/run_generate_hosts.sh

# Check what devices were found (last 20 lines)
tail -20 /srv/tplink-deco/log/output.log

# View current hosts entries
grep "TPLink Device List" -A 50 /etc/hosts

# Re-run bootstrap to update all files
wget -O bootstrap.py https://raw.githubusercontent.com/your-username/tplink-deco-poller/main/bootstrap.py
sudo python3 bootstrap.py
```

## 🚨 Troubleshooting

### Script Issues
```bash
# Check detailed logs
tail -f /srv/tplink-deco/log/output.log

# Test connectivity to router
ping 192.168.1.1  # Replace with your gateway IP

# Verify virtual environment packages
/srv/tplink-deco/venv/bin/pip list | grep tplinkrouterc6u

# Check configuration
cat /srv/tplink-deco/tplink.env
```

### Common Issues

| Problem | Solution |
|---------|----------|
| **Connection refused** | Verify `TPLINK_GATEWAY` IP address |
| **Authentication failed** | Check `TPLINK_PASSWORD` in tplink.env |
| **No devices found** | Ensure router has connected devices |
| **Permission denied** | Run with `sudo` or check file permissions |
| **Module not found** | Re-run bootstrap script to fix virtual environment |

### AdGuard Integration
```bash
# Check if AdGuard is running
systemctl status AdGuardHome

# View AdGuard logs
journalctl -u AdGuardHome -f

# Restart AdGuard (if needed)
sudo systemctl restart AdGuardHome
```

## 🔒 Security

- **Credentials**: Router password stored in `/srv/tplink-deco/tplink.env` with `600` permissions (root only)
- **Virtual Environment**: Python packages isolated from system
- **File Permissions**: All files owned by root with appropriate permissions
- **Logging**: No sensitive information logged in plain text

## 🔄 Updates

**To update to the latest version:**
```bash
# Re-download and run bootstrap
wget -O bootstrap.py https://raw.githubusercontent.com/your-username/tplink-deco-poller/main/bootstrap.py
sudo python3 bootstrap.py
```

The bootstrap script is idempotent and will:
- ✅ Preserve your configuration
- ✅ Update all script files
- ✅ Upgrade Python packages
- ✅ Maintain existing cron jobs

## 📊 Monitoring

```bash
# Monitor log file size
du -sh /srv/tplink-deco/log/

# Check last execution time
stat /etc/hosts

# View recent executions
grep "generate_hosts" /var/log/syslog | tail -5

# Monitor hosts file changes
watch -d cat /etc/hosts
```

## 🏗️ Development

**Repository Structure:**
```
tplink-deco-poller/
├── bootstrap.py              # Single download/install script
├── generate_hosts.py         # Main hosts generation logic  
├── run_generate_hosts.sh     # Runner with logging/locking
├── requirements.txt          # Python dependencies
└── readme.MD                 # This file
```

**To contribute:**
1. Fork the repository
2. Make your changes
3. Test with the bootstrap script
4. Submit a pull request

---

## ⚡ Quick Reference

| Command | Purpose |
|---------|----------|
| `wget bootstrap.py && sudo python3 bootstrap.py` | **Install everything** |
| `sudo /srv/tplink-deco/run_generate_hosts.sh` | **Run manually** |
| `tail -f /srv/tplink-deco/log/output.log` | **View live logs** |
| `sudo nano /srv/tplink-deco/tplink.env` | **Edit config** |
| `cat /etc/hosts` | **View generated hosts** |
| `crontab -l` | **View cron schedule** |

---

**🎯 Need help?** Open an issue on GitHub with:
- Your router model
- Error messages from logs  
- Contents of `/srv/tplink-deco/log/output.log`
