"""
simulador_llm.py — Camada explicativa APENAS.

O LLM recebe as métricas DETERMINÍSTICAS já calculadas e gera
uma explicação em linguagem natural contextualizada.

Isso resolve o problema de "dois sistemas de justiça":
  - Métricas são sempre geradas pelo motor determinístico
  - LLM produz apenas texto explicativo
  - O resultado da simulação não depende de disponibilidade de API
"""
import json
import httpx
from app.services.config import OPENROUTER_KEY, OPENROUTER_MODEL, OPENROUTER_BASE, has_api_key


PROMPT_EXPLICATIVO = """Voce e um analista de politicas publicas. Sua funcao eh EXPLICAR os resultados
de uma simulacao de impacto, e NAO criar as metricas (elas ja foram calculadas).

Proposta analisada:
Titulo: {titulo}
Regiao: {regiao} / {bioma}
ODS vinculados: {ods}
Orcamento: R$ {orcamento:,.0f}

Contexto regional:
{contexto}

Metricas calculadas (deterministicas):
{metricas}

Com base nos dados acima, escreva UM PARAGRAFO CURTO explicando:
1. Por que os impactos sao positivos ou negativos
2. Qual fator contextual mais influenciou os resultados
3. O que a proposta acerta e o que poderia ser melhorado

Nao repita os numeros das metricas. Foque na interpretacao qualitativa."""


async def explicar_com_llm(
    titulo: str,
    descricao: str,
    problema: str,
    solucao: str,
    orcamento: float,
    regiao: str,
    bioma: str,
    ods: list[int],
    contexto: dict,
    metricas: dict,
) -> str | None:
    if not has_api_key():
        return None

    prompt = PROMPT_EXPLICATIVO.format(
        titulo=titulo,
        descricao=descricao[:500],
        problema=problema[:300],
        solucao=solucao[:300],
        orcamento=orcamento,
        regiao=regiao,
        bioma=bioma,
        ods=ods,
        contexto=json.dumps(contexto, ensure_ascii=False, indent=2)[:2000],
        metricas=json.dumps(metricas, ensure_ascii=False, indent=2),
    )

    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"{OPENROUTER_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": "Voce explica simulacoes de politicas publicas. Responda APENAS um paragrafo curto."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 300,
            },
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
