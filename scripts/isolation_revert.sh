#!/usr/bin/env bash
# Revert isolation profile: restore previous CPU governors if backup exists

set -euo pipefail

BACKUP_FILE="data/results/_server_state/governor_backup.txt"

if [[ -f "$BACKUP_FILE" ]] && command -v cpupower >/dev/null 2>&1; then
  echo "Restoring CPU governors from $BACKUP_FILE (sudo may prompt)" >&2
  while read -r CPU GOV; do
    [[ -z "$CPU" || -z "$GOV" ]] && continue
    sudo bash -c "echo $GOV > /sys/devices/system/cpu/$CPU/cpufreq/scaling_governor" || true
  done < "$BACKUP_FILE"
  echo "Done."
else
  echo "No backup file or cpupower missing; nothing to revert." >&2
fi
