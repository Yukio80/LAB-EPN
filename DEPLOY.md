# Deploy

## Opcao 1: Railway (recomendado, 3 cliques)

1. Crie conta em https://railway.app (use GitHub)
2. Clique "New Project" → "Deploy from GitHub repo"
3. Selecione `Yukio80/LAB-EPN`
4. Railway detecta `railway.toml` automaticamente
5. Acesse o URL gerado

Apos o deploy, rode o seed no console do Railway:
```bash
cd /app && python scripts/seed_demo.py
```

## Opcao 2: Fly.io

```bash
# 1. Instale flyctl e crie conta
curl -fsSL https://fly.io/install.sh | sh
flyctl auth signup

# 2. Configure e deploy
flyctl launch --no-deploy
flyctl secrets set DATABASE_URL=sqlite:////data/lab-epn.db
flyctl deploy

# 3. Seed
flyctl ssh console -C "python /app/scripts/seed_demo.py"
```

## Opcao 3: Docker

```bash
docker build -t lab-epn .
docker run -p 8000:8000 lab-epn
```

## Variaveis de ambiente

| Variavel | Obrigatoria | Default | Descricao |
|---|---|---|---|
| `DATABASE_URL` | Nao | `sqlite:////data/lab-epn.db` | URL do banco |
| `OPENROUTER_API_KEY` | Nao | - | Chave LLM (opcional) |
| `PORT` | Sim (Railway) | 8000 | Porta do servidor |

Acesse em http://localhost:8000 (ou URL do provedor).
