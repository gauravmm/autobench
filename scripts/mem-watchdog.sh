#!/usr/bin/env bash
# Unified-memory watchdog for GB10 (DGX Spark) benchmark runs.
#
# WHY: CPU and GPU share ONE 121 GB pool. A vLLM run reserves ~0.85·121 GB of KV up front,
# then high-concurrency CUDA-graph capture + activation buffers pile on TOP of that reservation
# as --max-num-seqs grows. Past ~conc-64 at ctx 65536 the free headroom collapses to a few GB and
# the box HARD-CRASHES/reboots (no graceful OOM-kill — a GPU unified alloc that can't be satisfied
# takes the kernel down). Observed 2026-07-04: gemma-mtp c128 ran at ~4 GB free, c256 at ~0.2 GB
# free, and qwen-mtp c64 rebooted the machine.
#
# This polls MemAvailable fast and SIGKILLs the serving container the instant free memory drops
# below a floor — converting a machine crash into a killed container + a recorded "memory ceiling".
# Run it in the BACKGROUND before launching the serving container so it is armed during load/warmup
# (that is when graph capture spikes memory), not just during the benchmark.
#
# Usage: mem-watchdog.sh [floor_gb] [name_pattern] [poll_s]
#   floor_gb     trip when MemAvailable < this many GB (default 6)
#   name_pattern docker name substring to kill on breach (default "vllm-")
#   poll_s       sample interval seconds (default 0.25)
# Env: WATCHDOG_TRIPFILE (default /tmp/mem-watchdog.trip) — written on trip, removed at arm.
# Exit: 0 = stopped externally; 42 = tripped (container killed).
set -euo pipefail
FLOOR_GB="${1:-6}"
PATTERN="${2:-vllm-}"
POLL="${3:-0.25}"
FLOOR_KB=$(awk -v g="$FLOOR_GB" 'BEGIN{printf "%d", g*1024*1024}')
TRIPFILE="${WATCHDOG_TRIPFILE:-/tmp/mem-watchdog.trip}"
rm -f "$TRIPFILE"
mintrack=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
echo "==> mem-watchdog armed: floor=${FLOOR_GB}GB pattern='$PATTERN' poll=${POLL}s (MemTotal ~121GB, idle avail $(awk -v k=$mintrack 'BEGIN{printf "%.1f", k/1024/1024}')GB)"
while :; do
  avail=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
  [ "$avail" -lt "$mintrack" ] && mintrack=$avail
  if [ "$avail" -lt "$FLOOR_KB" ]; then
    ts=$(date "+%Y-%m-%d %H:%M:%S %z")
    availgb=$(awk -v k="$avail" 'BEGIN{printf "%.2f", k/1024/1024}')
    echo "!! WATCHDOG TRIP $ts MemAvailable=${availgb}GB < floor ${FLOOR_GB}GB — SIGKILL '$PATTERN' containers NOW"
    victims=$(docker ps --filter "name=$PATTERN" -q)
    [ -n "$victims" ] && docker kill $victims >/dev/null 2>&1 || true
    echo "tripped_at=$ts MemAvailable_gb=$availgb floor_gb=$FLOOR_GB killed=[$(echo $victims|tr '\n' ' ')]" > "$TRIPFILE"
    # keep reaping anything that respawns for a couple seconds, then exit
    for i in $(seq 1 8); do sleep "$POLL"; v=$(docker ps --filter "name=$PATTERN" -q); [ -n "$v" ] && docker kill $v >/dev/null 2>&1 || true; done
    exit 42
  fi
  sleep "$POLL"
done
