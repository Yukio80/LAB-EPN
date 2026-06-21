#!/bin/bash
# deploy.sh — Deploy automatico do LAB-EPN
# Uso: bash deploy.sh [--anyclaw | --railway | --fly]
set -euo pipefail

cd "$(dirname "$0")"

case "${1:-}" in
  --anyclaw)
    echo "=== Deploy frontend no Anyclaw ==="
    cd frontend
    rm -f ../_deploy.zip
    zip -r ../_deploy.zip . -x "*.git*"
    cd ..
    ZIP_B64=$(base64 < _deploy.zip | tr -d '\n')
    URL=$(curl -s --max-time 15 -X POST https://anyclaw.store/api/deploy \
      -H "Content-Type: application/json" \
      -d "{\"app_id\":\"lab-epn-pangeia\",\"zip_b64\":\"$ZIP_B64\",\"app_type\":\"web_app\",\"site_map\":[\"/\"]}" \
      | python3 -c "import sys,json; print(json.load(sys.stdin).get('claim_url',''))")
    echo "Frontend: $URL"
    rm -f _deploy.zip
    ;;

  --tunnel)
    echo "=== Iniciando tunnel ==="
    pkill -f "nokey@localhost.run" 2>/dev/null || true
    ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
      -R 80:localhost:8765 nokey@localhost.run 2>/dev/null \
      | grep -o 'https://[^ ]*\.lhr\.life' \
      | head -1 > /tmp/tunnel_url.txt &
    sleep 6
    TUNNEL_URL=$(cat /tmp/tunnel_url.txt)
    echo "Tunnel: $TUNNEL_URL"
    # Atualiza frontend
    sed -i "s|window.API_URL = '[^']*'|window.API_URL = '$TUNNEL_URL'|" frontend/index.html
    echo "Frontend atualizado. Rode: bash $0 --anyclaw"
    ;;

  --railway)
    echo "=== Deploy no Railway ==="
    echo "1. Crie conta em https://railway.app"
    echo "2. Conecte o repositorio GitHub"
    echo "3. Railway detecta railway.toml. Deploy automatico."
    echo "4. No console Railway: python scripts/seed_demo.py"
    echo "5. URL gerado automaticamente"
    ;;

  --fly)
    echo "=== Deploy no Fly.io ==="
    if ! command -v flyctl &>/dev/null; then
      curl -fsSL https://fly.io/install.sh | sh
    fi
    if ! flyctl auth whois &>/dev/null; then
      flyctl auth signup
    fi
    flyctl launch --no-deploy
    flyctl secrets set DATABASE_URL=sqlite:////data/lab-epn.db
    flyctl deploy
    flyctl ssh console -C "python /app/scripts/seed_demo.py"
    flyctl open
    ;;

  *)
    echo "Uso: bash deploy.sh [--anyclaw | --tunnel | --railway | --fly]"
    echo ""
    echo "  --anyclaw   Deploy frontend no Anyclaw Store"
    echo "  --tunnel    Inicia tunnel e atualiza API_URL no frontend"
    echo "  --railway   Instrucoes para deploy no Railway"
    echo "  --fly       Deploy completo no Fly.io"
    ;;
esac
