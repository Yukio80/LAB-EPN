#!/bin/bash
while true; do
  ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 nokey@localhost.run 2>/dev/null | grep -o 'https://[^ ]*\.lhr\.life' > /tmp/tunnel_url.txt
  sleep 5
done
