#!/bin/bash
# Mantem backend + tunnel ativos. Roda: nohup bash watchdog.sh > /dev/null 2>&1 &
cd /root/LAB-EPN

while true; do
  if ! pgrep -f "uvicorn.app.main" > /dev/null; then
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8765 > /tmp/uvicorn_out.log 2>&1 &
    echo "[$(date)] Backend reiniciado" >> /tmp/watchdog.log
  fi

  if ! pgrep -f "nokey@localhost.run" > /dev/null; then
    nohup ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
      -R 80:localhost:8765 nokey@localhost.run > /tmp/tunnel_raw.log 2>&1 &
    echo "[$(date)] Tunnel reiniciado" >> /tmp/watchdog.log
  fi

  URL=$(grep -o 'https://[^ ]*\.lhr\.life' /tmp/tunnel_raw.log 2>/dev/null | tail -1)
  if [ -n "$URL" ]; then
    echo "[$(date)] Tunnel URL: $URL" >> /tmp/watchdog.log
  fi

  sleep 30
done
