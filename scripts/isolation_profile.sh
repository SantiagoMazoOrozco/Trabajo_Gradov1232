#!/usr/bin/env bash
# Apply a lightweight isolation profile for experiments on Linux.
# - Sets CPU governor to 'performance' for all CPUs (requires sudo and cpupower)
# - Optionally sets process priority/IO priority for a given command
# - Saves previous governor state to data/results/_server_state/governor_backup.txt

set -euo pipefail

STATE_DIR="data/results/_server_state"
mkdir -p "$STATE_DIR"
BACKUP_FILE="$STATE_DIR/governor_backup.txt"

if command -v cpupower >/dev/null 2>&1; then
  echo "Saving current governors to $BACKUP_FILE" >&2
  : > "$BACKUP_FILE"
  for CPUF in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do
    CPU=$(echo "$CPUF" | sed -E 's#.*/cpu([0-9]+)/.*#\1#')
    CUR=$(cat "$CPUF" 2>/dev/null || echo "unknown")
    echo "cpu$CPU $CUR" >> "$BACKUP_FILE"
  done
  echo "Setting governor=performance (sudo may prompt)" >&2
  sudo cpupower frequency-set -g performance || echo "cpupower failed; continuing without governor change" >&2
else
  echo "cpupower not available; skipping governor changes" >&2
fi

echo "Isolation profile applied. You can now run your experiment with taskset/nice, e.g.:" >&2
echo "  taskset -c 0-1 nice -n 5 bash scripts/run_experiment.sh" >&2
