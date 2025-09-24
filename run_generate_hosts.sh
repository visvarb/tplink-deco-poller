#!/bin/bash

ENV_FILE="/srv/tplink-deco/tplink.env"
LOG_FILE="/srv/tplink-deco/log/output.log"
SCRIPT="/srv/tplink-deco/generate_hosts.py"

# Exit if env file missing
[ -f "$ENV_FILE" ] || { echo "Env file missing"; exit 1; }

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Prevent multiple instances
(
  flock -n 200 || exit 0

  # Load environment
  set -a
  source "$ENV_FILE"
  set +a

  # Run script safely using virtual environment Python
  /srv/tplink-deco/venv/bin/python "$SCRIPT" >> "$LOG_FILE" 2>&1
) 200>/var/lock/tplink.lock
