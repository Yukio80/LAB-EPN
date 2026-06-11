import json
import math
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4

from app.services.dados_brasil import dados_bioma, indicadores_compostos, escala_log
from app.services.pesos_ods import obter_peso, calcular_mult_contexto, versao_pesos
from app.services.simulador_llm import explicar_com_llm


class SimulacaoRequest(BaseModel):
    proposta_id: str
    titulo: str
    descricao: str
    problema: str = ""
    solucao: str = ""
    orcamento: float
    localizacao: dict
    ods: list[int]


class SimulacaoResponse(BaseModel):
    id_simulacao: UUID = Field(default_factory=uuid4)
    status: str
    metricas: dict
    resumo_executivo: str
    contexto_regional: dict = Field(default_factory=dict)
    motor_usado: str = "pangeia_core"
    modelo_versao: str = "v1.1"
    pesos_ods_versao: str = Field(default_factory=versao_pesos)
    metodologia: dict = Field(default_factory=dict)
    hash_ipfs: Optional[str] = None


async def chamar_motor_pangeia(request: SimulacaoRequest) -> SimulacaoResponse:
    """
    Motor de simulação — cálculo determinístico auditável.

    Metodologia:
      1. Escala logarítmica no orçamento → retornos decrescentes
      2. Pesos ODS versionados (pesos_ods.py v{versao_pesos()})
      3. Fatores de interação contextual (sinergia título + condições regionais)
      4. Baseline pré-impacto a partir de indicadores reais (UF + bioma + município)
      5. LLM usado APENAS como camada explicativa (não gera métricas)

    Isto garante que duas simulações com os mesmos inputs
    produzam EXATAMENTE os mesmos outputs, independente de
    disponibilidade de API externa.
    """
    bioma = request.localizacao.get("bioma", "")
    uf = request.localizacao.get("estado", "")
    municipio = request.localizacao.get("municipio", "")

    contexto = await dados_bioma(bioma) if bioma else {}
    if uf:
        comp = indicadores_compostos(uf, bioma, municipio)
        contexto.update(comp)
        contexto["uf"] = uf
        contexto["regiao"] = request.localizacao.get("regiao", "")

    metricas = _calcular_metricas(request, contexto)
    resumo = await _gerar_explicacao(request, contexto, metricas)

    return SimulacaoResponse(
        status="simulada",
        contexto_regional=contexto,
        metricas=metricas,
        resumo_executivo=resumo,
        motor_usado=f"deterministico_{uf.lower() or bioma.lower() or 'br'}",
        metodologia={
            "escala_orcamento": "log2(1 + orcamento / 50M)",
            "pesos_ods": f"pesos_ods.py v{versao_pesos()}",
            "indicadores_base": "IBGE/PNAD/PNUD 2023-2024",
            "municipio_considerado": bool(municipio),
            "llm_usado_para": "explicacao_em_linguagem_natural_apenas",
        },
    )


def _calcular_metricas(request: SimulacaoRequest, contexto: dict) -> dict:
    uf = contexto.get("uf", request.localizacao.get("estado", ""))
    idh = contexto.get("idh", 0.7)
    gini = contexto.get("gini", 0.55)
    escolaridade = contexto.get("escolaridade", 7.0)
    vulnerabilidade = contexto.get("indice_vulnerabilidade", 0.4)
    pib_base = contexto.get("pib_per_capita", 15000 * idh)
    estresse_hidrico = contexto.get("estresse_hidrico", 0.5)
    risco_incendio = contexto.get("risco_incendio", 0.3)
    cobertura_vegetal = contexto.get("cobertura_vegetal_pct", 50)
    agro_pct = contexto.get("pib_agropecuaria_pct", 15)

    # Camada 1: escala logarítmica no orçamento
    fator_orcamento = escala_log(request.orcamento)
    fator_orcamento = min(fator_orcamento, 4.0)  # teto de ~R$ 7.5B

    titulo_lower = request.titulo.lower()

    # Calcula delta por métrica agregando pesos dos ODS + contexto
    def delta_ods(metrica: str, default: float = 0.0) -> float:
        total = 0.0
        for ods_id in request.ods:
            peso_base = obter_peso(ods_id, metrica, 0.0)
            mult = calcular_mult_contexto(ods_id, contexto, titulo_lower)
            total += peso_base * mult
        return total

    # Deltas base (escala orçamentária)
    delta_desc_base = -0.02 * fator_orcamento
    delta_emp_base = 0.02 * fator_orcamento
    delta_conf_base = 0.01 * fator_orcamento
    delta_conflito_base = -0.02 * fator_orcamento
    delta_pib_base = 0.01 * fator_orcamento

    # Soma contribuições dos ODS
    delta_desc = max(-0.5, min(0.0, delta_desc_base + delta_ods("desigualdade")))
    delta_emp = max(0.0, min(0.5, delta_emp_base + delta_ods("emprego")))
    delta_conf = max(0.0, min(0.4, delta_conf_base + delta_ods("confianca")))
    delta_conflito = max(-0.4, min(0.0, delta_conflito_base + delta_ods("conflito")))
    impacto_pib = max(0.0, min(0.3, delta_pib_base + delta_ods("pib")))

    # Interação: estresse hídrico + proposta de água
    if estresse_hidrico > 0.6 and ("agua" in titulo_lower or "saneamento" in titulo_lower):
        delta_conf *= 1.2
        delta_conflito *= 1.3
    if cobertura_vegetal < 40 and "reflorestamento" in titulo_lower:
        delta_desc *= 1.15
        delta_emp *= 1.15
    if gini > 0.56 and "desigualdade" in titulo_lower:
        delta_desc *= 1.25
    if risco_incendio > 0.5 and "clima" in titulo_lower:
        delta_conflito *= 1.2

    # Baselines pré-impacto (documentados)
    desigualdade_antes = round(vulnerabilidade * 0.85, 2)
    emprego_antes = round(idh * 0.45 + (1 - gini) * 0.35 - (agro_pct / 100) * 0.1, 2)
    confianca_antes = round(idh * 0.4 + escolaridade * 0.03 + (1 - gini) * 0.2, 2)
    conflito_antes = round(
        min((1 - idh) * 0.4 + gini * 0.3 + estresse_hidrico * 0.2 + risco_incendio * 0.1, 0.9),
        2,
    )

    return {
        "indice_desigualdade": {
            "antes": desigualdade_antes,
            "depois": round(max(0.05, desigualdade_antes + delta_desc), 2),
            "delta": round(delta_desc, 3),
        },
        "emprego_local": {
            "antes": emprego_antes,
            "depois": round(min(0.95, emprego_antes + delta_emp), 2),
            "delta": round(delta_emp, 3),
        },
        "indice_confianca_social": {
            "antes": confianca_antes,
            "depois": round(min(0.95, confianca_antes + delta_conf), 2),
            "delta": round(delta_conf, 3),
        },
        "probabilidade_conflito": {
            "antes": conflito_antes,
            "depois": round(max(0.05, conflito_antes + delta_conflito), 2),
            "delta": round(delta_conflito, 3),
        },
        "pib_per_capita": {
            "antes": round(pib_base, 0),
            "depois": round(pib_base * (1 + impacto_pib), 0),
            "delta": round(pib_base * impacto_pib, 0),
        },
    }


async def _gerar_explicacao(request: SimulacaoRequest, contexto: dict, metricas: dict) -> str:
    """
    LLM usado APENAS para gerar explicação em linguagem natural.
    As métricas são sempre determinísticas e independentes do LLM.
    Se o LLM não estiver disponível, gera texto template.
    """
    uf = contexto.get("uf", request.localizacao.get("estado", "BR"))
    bioma = request.localizacao.get("bioma", "")
    idh = contexto.get("idh", 0.7)
    gini = contexto.get("gini", 0.55)
    orcamento = request.orcamento

    resumo_template = (
        f"Simulacao deterministica para {uf.upper()} ({bioma}, IDH {idh}, GINI {gini}). "
        f"Orcamento de R$ {orcamento:,.0f} com escala log. "
        f"Resultados: desigualdade {metricas['indice_desigualdade']['delta']*100:+.1f}%, "
        f"emprego +{metricas['emprego_local']['delta']*100:.1f}%, "
        f"confianca +{metricas['indice_confianca_social']['delta']*100:.1f}%, "
        f"conflito {metricas['probabilidade_conflito']['delta']*100:+.1f}%, "
        f"PIB pc +R$ {metricas['pib_per_capita']['delta']:,.0f}. "
        "Modelo deterministico — LLM usado apenas para questa explicacao."
    )

    explicacao = await explicar_com_llm(
        titulo=request.titulo,
        descricao=request.descricao,
        problema=request.problema,
        solucao=request.solucao,
        orcamento=orcamento,
        regiao=request.localizacao.get("regiao", ""),
        bioma=bioma,
        ods=request.ods,
        contexto=contexto,
        metricas=metricas,
    )
    return explicacao or resumo_template
