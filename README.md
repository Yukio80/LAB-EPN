# LAB-EPN + Pangeia

Plataforma de simulação de políticas públicas que integra dados governamentais brasileiros com modelos de impacto para qualificar a tomada de decisão participativa.

## Arquitetura

```
Frontend (Vue 3 + Tailwind CDN)
        │ POST /propostas {estado, bioma, orcamento, ods}
        ▼
FastAPI (5 REST + 6 admin endpoints)
        │
        ▼
chamar_motor_pangeia()
        │
        ├─ dados_brasil.py     → 27 UFs, 6 biomas, 15+ municípios
        ├─ pesos_ods.py        → 17 ODS versionados (v1.0)
        ├─ [determinístico]    → escala log, pesos ODS, contexto regional
        └─ [LLM opcional]      → explicação em linguagem natural (OpenRouter)
```

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / FastAPI / SQLAlchemy / SQLite |
| Frontend | Vue 3 (CDN) + Tailwind CSS (CDN) — sem build step |
| Contrato | Solidity ^0.8.20 — QuadraticVote.sol |
| LLM | OpenRouter (gpt-4o-mini) — apenas camada explicativa |
| Deploy | Anyclaw (frontend) / serveo.net (túnel API) |

## Estrutura

```
app/
  main.py              — FastAPI app, CORS, static mount
  database.py          — SQLAlchemy engine + SessionLocal
  models/proposta.py   — ORM + Pydantic schemas
  routes/
    propostas.py       — CRUD + simular + publicar
    admin.py           — Painel de Compliance (pesos, revisão, auditoria)
  services/
    config.py          — env loader (.env automático)
    dados_brasil.py    — IBGE API + indicadores UF/bioma/município
    simulacao.py       — Motor determinístico v1.1
    simulador_llm.py   — LLM explicativo (não gera métricas)
    pesos_ods.py       — Tabela versionada de 17 ODS
frontend/
  index.html           — SPA Vue 3 + Tailwind
  api.js               — HTTP client
contratos/
  QuadraticVote.sol    — Votação quadrática on-chain
scripts/
  migrar_propostas.py  — Reavaliação de propostas legadas
```

## Instalação

```bash
git clone https://github.com/Yukio80/LAB-EPN.git
cd LAB-EPN
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # opcional: configurar OpenRouter
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API

### Propostas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/propostas` | Lista todas as propostas |
| POST | `/propostas` | Cria nova proposta |
| GET | `/propostas/{id}` | Detalhe da proposta |
| POST | `/propostas/{id}/simular` | Executa simulação de impacto |
| POST | `/propostas/{id}/publicar` | Publica para votação |

### Admin / Compliance
| Método | Rota | Descrição |
|---|---|---|
| GET | `/admin/dashboard` | Métricas do sistema |
| GET | `/admin/pesos` | Tabela de pesos ODS (17) |
| PUT | `/admin/pesos` | Atualiza peso (com justificativa auditada) |
| GET | `/admin/auditoria` | Log de alterações |
| GET | `/admin/propostas/pendentes` | Propostas aguardando validação |
| POST | `/admin/propostas/{id}/validar` | Aprova ou rejeita proposta |
| GET | `/admin/votacoes` | Votações ativas |

## Modelo de Simulação v1.1

### Escala de orçamento
```
fator = log2(1 + orcamento / 50M)
```
Resultado: R$50M → 1.0, R$250M → 2.32, R$500M → 3.17 (retornos decrescentes)

### Pesos ODS
Cada ODS tem coeficientes para 5 métricas (`desigualdade`, `emprego`, `confianca`, `conflito`, `pib`) e condições de sinergia contextual (título + indicadores regionais). Tabela versionada e auditável via `PUT /admin/pesos`.

### Índice de Vulnerabilidade
```
vulnerabilidade = 0.40*(1 - IDH) + 0.35*GINI + 0.25*(1 - escolaridade/10)
```
Composição documentada e retornada no campo `_composicao_vulnerabilidade` do contexto.

### Cobertura de Dados
- **27 UFs**: população, PIB per capita, IDH, GINI, escolaridade, expectativa de vida, área
- **6 biomas**: área, desmatamento anual, estoque de carbono, estresse hídrico, biodiversidade, risco de incêndio, cobertura vegetal, % agropecuária
- **15 municípios catalogados**: com indicadores próprios (fallback para UF)
- **IBGE Localidades (live)**: regiões, estados, municípios via API

## Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `OPENROUTER_API_KEY` | Não | — | Chave para LLM explicativo (OpenRouter) |
| `OPENROUTER_MODEL` | Não | `openai/gpt-4o-mini` | Modelo do LLM |

O `.env` é carregado automaticamente por `config.py`. Sem a chave, o sistema funciona no modo 100% determinístico.

## Migração (propostas legadas)

```bash
source .venv/bin/activate
python scripts/migrar_propostas.py            # executa reavaliação
python scripts/migrar_propostas.py --dry-run  # apenas simula
```

## Licença

MIT
