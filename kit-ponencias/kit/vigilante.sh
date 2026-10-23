#!/bin/bash
# vigilante.sh <log> <comando…>
# Corre un comando pesado (whisper, render) y lo detiene si la Mac se está quedando sin memoria,
# antes de que se congele. Umbrales (se pueden cambiar en .env):
#   VIGILANTE_SWAP_MB  swap libre mínimo cuando ya hay swap en uso (300 MB por omisión)
#   VIGILANTE_LIBRE    % de memoria libre mínimo según memory_pressure (5 % por omisión)
log=$1; shift
SWAP_MIN=${VIGILANTE_SWAP_MB:-300}
LIBRE_MIN=${VIGILANTE_LIBRE:-5}

set -m                      # el comando va en su propio grupo de procesos
"$@" &
pid=$!
while kill -0 "$pid" 2>/dev/null; do
  sleep 3
  # vm.swapusage: total = 2048.00M  used = 1500.00M  free = 548.00M
  read -r total free < <(sysctl -n vm.swapusage | awk '{gsub("M","",$3); gsub("M","",$9); print int($3), int($9)}')
  libre=$(memory_pressure -Q 2>/dev/null | awk -F': ' '/free percentage/ {gsub("%","",$2); print int($2)}')
  motivo=""
  if [ "${total:-0}" -gt 0 ] && [ "${free:-0}" -lt "$SWAP_MIN" ]; then motivo="swap libre ${free} MB < ${SWAP_MIN} MB"; fi
  if [ -n "$libre" ] && [ "$libre" -lt "$LIBRE_MIN" ]; then motivo="memoria libre ${libre}% < ${LIBRE_MIN}%"; fi
  if [ -n "$motivo" ]; then
    echo "$(date '+%F %T') vigilante: $motivo, detengo «$1» para no congelar la Mac" | tee -a "$log" >&2
    kill -TERM -- "-$pid" 2>/dev/null; sleep 2; kill -KILL -- "-$pid" 2>/dev/null
    exit 3
  fi
done
wait "$pid"
