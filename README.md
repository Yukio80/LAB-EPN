# LAB-EPN + Pangeia

**Demo online:** [https://lab-epn-pangeia.anyclaw.store](https://lab-epn-pangeia.anyclaw.store)

**Backend (API + Swagger):** [https://lab-epn-production.up.railway.app](https://lab-epn-production.up.railway.app) · [`/docs`](https://lab-epn-production.up.railway.app/docs)

**Anyclaw Store:** [https://anyclaw.store/pixelotter-8/lab-epn-pangeia](https://anyclaw.store/pixelotter-8/lab-epn-pangeia)

Acesse, veja 5 propostas pre-carregadas com simulacao, e vote nas 2 em votacao on-chain.

Plataforma de simulacao de politicas publicas brasileiras. Crie propostas, simule impacto com dados reais (IBGE, PNAD, PNUD), vote on-chain e acompanhe com painel de compliance.

---

## Fluxo principal (3 passos)

1. **Crie** uma proposta — descreva o problema, a solucao, regiao, orcamento e ODS vinculados
2. **Simule** — o motor Pangeia calcula impacto em 5 metricas (desigualdade, emprego, confianca, conflito, PIB) usando dados reais da UF/bioma/municipio
3. **Publique** para votacao quadratica on-chain — qualquer pessoa pode votar com creditos

---

## Para quem e isso?

- **Jornalista de dados** — quer embasar reportagens sobre politicas publicas com simulacoes reproduziveis e dados abertos. Pode criar propostas, simular cenarios e exportar metricas.
- **Pesquisador academico** — precisa de um ambiente auditavel para modelar impacto de politicas. O motor deterministico garante reproducibilidade; os pesos ODS sao versionados e editaveis.
- **Organizacao da sociedade civil** — quer qualificar sua incidencia politica com dados. Pode prototipar propostas, simular antes de apresentar a governos e mobilizar votacao.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / FastAPI / SQLAlchemy / SQLite |
| Frontend | Vue 3 (CDN) + Tailwind CSS (CDN) — sem build step |
| Contrato | Solidity ^0.8.20 — QuadraticVote.sol |
| LLM | OpenRouter (opcional) — apenas camada explicativa |
| Deploy | Railway (backend) / Anyclaw (frontend) |

---

## Rodar localmente

```bash
git clone https://github.com/Yukio80/LAB-EPN.git
cd LAB-EPN
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_demo.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse http://localhost:8000. O frontend e servido como static file pelo proprio FastAPI.

---

## Deploy

### Railway (backend — ja no ar)

O backend esta implantado em [https://lab-epn-production.up.railway.app](https://lab-epn-production.up.railway.app).

```bash
railway login --browserless     # autentica com codigo no terminal
railway link --project LAB-EPN  # vincula o repositorio
railway up                      # ou: git push (auto-deploy via GitHub)
```

Variaveis de ambiente configuradas:

| Variavel | Valor |
|---|---|
| `DATABASE_URL` | `sqlite:///./lab-epn.db` |
| `OPENROUTER_API_KEY` | vazio (modo deterministico) |

O banco SQLite e efemero (resetado em restart), mas o auto-seed na inicializacao (`lifespan` em `app/main.py`) recria as 5 propostas + 2 votacoes automaticamente.

### Anyclaw (frontend)

```bash
# Atualizar e publicar:
zip -r app.zip frontend/
ZIP_B64=$(base64 < app.zip | tr -d '\n')
curl -X POST https://anyclaw.store/api/deploy \
  -H "Content-Type: application/json" \
  -d '{"app_id":"lab-epn-pangeia","zip_b64":"'$ZIP_B64'","app_type":"web_app"}'
```

Apos deploy, visite a claim URL gerada e confirme.

---

## Estrutura do projeto

```
app/
  main.py              — FastAPI app, CORS, static mount, auto-seed
  database.py          — SQLAlchemy engine (DATABASE_URL via env)
  models/proposta.py   — ORM + Pydantic schemas (10 status, 17 ODS)
  routes/
    propostas.py       — CRUD + simular + publicar
    admin.py           — Painel de Compliance (pesos ODS, revisao, auditoria)
    votacao.py         — Votacao on-chain
  services/
    config.py          — .env loader automatico
    dados_brasil.py    — 27 UFs, 6 biomas, 15+ municipios
    simulacao.py       — Motor deterministico v1.1 (escala log + pesos ODS)
    simulador_llm.py   — LLM explicativo (nao gera metricas)
    pesos_ods.py       — 17 ODS versionados com pesos auditaveis
    votacao_onchain.py — Simulador de contrato QuadraticVote (dev)
frontend/
  index.html           — SPA Vue 3 + Tailwind (inline)
scripts/
  seed_demo.py         — Popula banco com 5 propostas + simulacoes + votacao
contratos/
  QuadraticVote.sol    — Votacao quadratica on-chain
railway.toml           — Configuracao de build/deploy Railway
Procfile               — Start command Railway
```

---

## Simulacao

### Escala de orcamento
```
fator = log2(1 + orcamento / 50M)
```
R$50M → 1.0, R$250M → 2.32, R$500M → 3.17 (retornos decrescentes)

### Pesos ODS
17 ODS com coeficientes para 5 metricas (desigualdade, emprego, confianca, conflito, PIB). Versionados e editaveis via `PUT /admin/pesos` com auditoria.

### Cobertura de dados
- **27 UFs**: populacao, PIB pc, IDH, GINI, escolaridade, expectativa de vida
- **6 biomas**: desmatamento, carbono, estresse hidrico, risco incendio, cobertura vegetal
- **15 municipios catalogados** com indicadores proprios (fallback para UF)
- **Resolucao geografica**: `municipal` (verde), `uf_fallback` (amarelo), `uf` (cinza)

---

## Seed de demonstracao

```bash
python scripts/seed_demo.py
```

Cria 5 propostas reais (saneamento no MA, reflorestamento no PA, educacao em AL, habitacao em SP, agricultura familiar na BA), todas simuladas, 2 em votacao on-chain.

---

## Licenca

MIT
