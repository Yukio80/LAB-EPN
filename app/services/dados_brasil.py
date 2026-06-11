import httpx
from typing import Optional, Any

IBGE_BASE = "https://servicodados.ibge.gov.br/api/v1"

# ─── Live APIs (IBGE Localidades) ───────────────────────────────

async def regioes() -> list[dict]:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{IBGE_BASE}/localidades/regioes")
        r.raise_for_status()
        return r.json()


async def estados(regiao_sigla: Optional[str] = None) -> list[dict]:
    url = f"{IBGE_BASE}/localidades/estados"
    if regiao_sigla:
        url = f"{IBGE_BASE}/localidades/regioes/{regiao_sigla}/estados"
    async with httpx.AsyncClient() as c:
        r = await c.get(url)
        r.raise_for_status()
        return r.json()


async def municipios(uf_sigla: str) -> list[dict]:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{IBGE_BASE}/localidades/estados/{uf_sigla}/municipios")
        r.raise_for_status()
        return r.json()


async def info_uf(uf_sigla: str) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{IBGE_BASE}/localidades/estados/{uf_sigla}")
        r.raise_for_status()
        return r.json()


# ─── Static indicators per UF (IBGE/PNAD/PNUD 2023-2024) ────────

DADOS_UF: dict[str, dict] = {
    "AC": {"populacao": 830018, "pib_per_capita": 18176, "idh": 0.710, "gini": 0.56, "expectativa_vida": 73.5, "escolaridade": 7.2, "area_km2": 164123},
    "AL": {"populacao": 3127494, "pib_per_capita": 17051, "idh": 0.684, "gini": 0.57, "expectativa_vida": 72.0, "escolaridade": 6.5, "area_km2": 27848},
    "AP": {"populacao": 877613, "pib_per_capita": 20288, "idh": 0.730, "gini": 0.54, "expectativa_vida": 74.1, "escolaridade": 7.8, "area_km2": 142471},
    "AM": {"populacao": 4142597, "pib_per_capita": 30696, "idh": 0.720, "gini": 0.55, "expectativa_vida": 73.8, "escolaridade": 7.5, "area_km2": 1559168},
    "BA": {"populacao": 14136783, "pib_per_capita": 21947, "idh": 0.691, "gini": 0.58, "expectativa_vida": 73.2, "escolaridade": 6.8, "area_km2": 564733},
    "CE": {"populacao": 8940588, "pib_per_capita": 19955, "idh": 0.708, "gini": 0.56, "expectativa_vida": 73.7, "escolaridade": 7.2, "area_km2": 148887},
    "DF": {"populacao": 2817381, "pib_per_capita": 80778, "idh": 0.824, "gini": 0.52, "expectativa_vida": 77.5, "escolaridade": 9.5, "area_km2": 5760},
    "ES": {"populacao": 3838363, "pib_per_capita": 37256, "idh": 0.756, "gini": 0.51, "expectativa_vida": 76.5, "escolaridade": 8.2, "area_km2": 46085},
    "GO": {"populacao": 7057120, "pib_per_capita": 35894, "idh": 0.737, "gini": 0.53, "expectativa_vida": 75.4, "escolaridade": 8.1, "area_km2": 340111},
    "MA": {"populacao": 6775152, "pib_per_capita": 14900, "idh": 0.676, "gini": 0.59, "expectativa_vida": 71.5, "escolaridade": 6.2, "area_km2": 329642},
    "MT": {"populacao": 3658649, "pib_per_capita": 43270, "idh": 0.725, "gini": 0.52, "expectativa_vida": 74.8, "escolaridade": 7.9, "area_km2": 903208},
    "MS": {"populacao": 2757013, "pib_per_capita": 39629, "idh": 0.742, "gini": 0.50, "expectativa_vida": 75.9, "escolaridade": 8.0, "area_km2": 357148},
    "MG": {"populacao": 20538503, "pib_per_capita": 35022, "idh": 0.743, "gini": 0.52, "expectativa_vida": 76.2, "escolaridade": 8.0, "area_km2": 586521},
    "PA": {"populacao": 8617021, "pib_per_capita": 20270, "idh": 0.690, "gini": 0.57, "expectativa_vida": 73.0, "escolaridade": 6.8, "area_km2": 1245803},
    "PB": {"populacao": 3974693, "pib_per_capita": 18025, "idh": 0.699, "gini": 0.56, "expectativa_vida": 73.4, "escolaridade": 7.0, "area_km2": 56585},
    "PR": {"populacao": 11444126, "pib_per_capita": 40507, "idh": 0.769, "gini": 0.49, "expectativa_vida": 77.5, "escolaridade": 8.5, "area_km2": 199308},
    "PE": {"populacao": 9058157, "pib_per_capita": 20939, "idh": 0.704, "gini": 0.57, "expectativa_vida": 73.6, "escolaridade": 7.1, "area_km2": 98076},
    "PI": {"populacao": 3269531, "pib_per_capita": 16166, "idh": 0.678, "gini": 0.59, "expectativa_vida": 71.8, "escolaridade": 6.3, "area_km2": 251577},
    "RJ": {"populacao": 16055174, "pib_per_capita": 43911, "idh": 0.767, "gini": 0.55, "expectativa_vida": 76.8, "escolaridade": 8.3, "area_km2": 43750},
    "RN": {"populacao": 3302739, "pib_per_capita": 20923, "idh": 0.713, "gini": 0.55, "expectativa_vida": 74.5, "escolaridade": 7.3, "area_km2": 52811},
    "RS": {"populacao": 10882506, "pib_per_capita": 41503, "idh": 0.762, "gini": 0.49, "expectativa_vida": 77.2, "escolaridade": 8.4, "area_km2": 281707},
    "RO": {"populacao": 1831352, "pib_per_capita": 29646, "idh": 0.710, "gini": 0.53, "expectativa_vida": 73.6, "escolaridade": 7.6, "area_km2": 237590},
    "RR": {"populacao": 652713, "pib_per_capita": 26740, "idh": 0.715, "gini": 0.54, "expectativa_vida": 73.4, "escolaridade": 7.7, "area_km2": 224273},
    "SC": {"populacao": 7610903, "pib_per_capita": 47215, "idh": 0.791, "gini": 0.47, "expectativa_vida": 78.1, "escolaridade": 8.7, "area_km2": 95731},
    "SP": {"populacao": 44411238, "pib_per_capita": 53270, "idh": 0.796, "gini": 0.50, "expectativa_vida": 77.8, "escolaridade": 8.8, "area_km2": 248197},
    "SE": {"populacao": 2109337, "pib_per_capita": 24737, "idh": 0.707, "gini": 0.55, "expectativa_vida": 73.3, "escolaridade": 7.0, "area_km2": 21925},
    "TO": {"populacao": 1601144, "pib_per_capita": 23083, "idh": 0.713, "gini": 0.54, "expectativa_vida": 74.2, "escolaridade": 7.5, "area_km2": 277621},
}


# ─── Static biome data (IBGE/INPE/MapBiomas) ────────────────────

BIOMAS: dict[str, dict] = {
    "Amazônia": {
        "area_km2": 4200000,
        "estados": ["AC", "AM", "AP", "MA", "MT", "PA", "RO", "RR", "TO"],
        "populacao_estimada": 25000000,
        "idh_medio": 0.683,
        "desmatamento_anual_km2": 5000,
        "carbono_estoque_t": 120000000000,
        "estresse_hidrico": 0.15,
        "biodiversidade": 0.95,
        "risco_incendio": 0.4,
        "cobertura_vegetal_pct": 82.0,
        "agua_superficie_pct": 8.5,
        "pib_agropecuaria_pct": 12.0,
    },
    "Caatinga": {
        "area_km2": 844453,
        "estados": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "populacao_estimada": 28000000,
        "idh_medio": 0.654,
        "desmatamento_anual_km2": 2000,
        "carbono_estoque_t": 5000000000,
        "estresse_hidrico": 0.85,
        "biodiversidade": 0.60,
        "risco_incendio": 0.3,
        "cobertura_vegetal_pct": 48.0,
        "agua_superficie_pct": 2.0,
        "pib_agropecuaria_pct": 25.0,
    },
    "Cerrado": {
        "area_km2": 2036448,
        "estados": ["BA", "DF", "GO", "MA", "MG", "MS", "MT", "PI", "PR", "SP", "TO"],
        "populacao_estimada": 30000000,
        "idh_medio": 0.720,
        "desmatamento_anual_km2": 7000,
        "carbono_estoque_t": 30000000000,
        "estresse_hidrico": 0.55,
        "biodiversidade": 0.75,
        "risco_incendio": 0.6,
        "cobertura_vegetal_pct": 53.0,
        "agua_superficie_pct": 4.5,
        "pib_agropecuaria_pct": 35.0,
    },
    "Mata Atlântica": {
        "area_km2": 1100000,
        "estados": ["AL", "BA", "CE", "ES", "GO", "MG", "MS", "MT", "PB", "PE", "PI", "PR", "RJ", "RN", "RS", "SC", "SE", "SP"],
        "populacao_estimada": 145000000,
        "idh_medio": 0.754,
        "desmatamento_anual_km2": 200,
        "carbono_estoque_t": 15000000000,
        "estresse_hidrico": 0.45,
        "biodiversidade": 0.85,
        "risco_incendio": 0.2,
        "cobertura_vegetal_pct": 12.0,
        "agua_superficie_pct": 6.0,
        "pib_agropecuaria_pct": 8.0,
    },
    "Pampa": {
        "area_km2": 176496,
        "estados": ["RS"],
        "populacao_estimada": 5000000,
        "idh_medio": 0.746,
        "desmatamento_anual_km2": 100,
        "carbono_estoque_t": 2000000000,
        "estresse_hidrico": 0.35,
        "biodiversidade": 0.55,
        "risco_incendio": 0.15,
        "cobertura_vegetal_pct": 33.0,
        "agua_superficie_pct": 5.0,
        "pib_agropecuaria_pct": 20.0,
    },
    "Pantanal": {
        "area_km2": 150355,
        "estados": ["MS", "MT"],
        "populacao_estimada": 1500000,
        "idh_medio": 0.700,
        "desmatamento_anual_km2": 500,
        "carbono_estoque_t": 8000000000,
        "estresse_hidrico": 0.40,
        "biodiversidade": 0.90,
        "risco_incendio": 0.7,
        "cobertura_vegetal_pct": 78.0,
        "agua_superficie_pct": 15.0,
        "pib_agropecuaria_pct": 30.0,
    },
}


# ─── Escala logarítmica para orçamento (Camada 1) ──────────────

import math

def escala_log(orcamento: float, baseline: float = 50e6) -> float:
    """
    Retorna fator de escala com retornos decrescentes.

    log2(1 + orcamento / baseline)

    Exemplos:
      R$  50M → 1.00
      R$ 100M → 1.58
      R$ 250M → 2.32  (vs 5.0 na escala linear)
      R$ 500M → 3.17  (vs 10.0 na escala linear)
      R$   1B → 3.91
    """
    return math.log2(1 + max(orcamento, 0) / baseline)


# ─── Dados municipais (IBGE Censo 2022 + PNUD) ──────────────────
# Resolução municipal para cidades com > 500k hab ou capitais.
# Quando o município não está listado, usa a média da UF.

DADOS_MUNICIPIO: dict[str, dict[str, dict]] = {
    "BA": {
        "Salvador":     {"populacao": 2417678, "pib_per_capita": 25234, "idh": 0.759, "gini": 0.62},
        "Juazeiro":     {"populacao": 215786,  "pib_per_capita": 18920, "idh": 0.677, "gini": 0.58},
        "Ilhéus":       {"populacao": 178703,  "pib_per_capita": 22340, "idh": 0.690, "gini": 0.57},
        "Feira de Santana": {"populacao": 616279, "pib_per_capita": 20150, "idh": 0.712, "gini": 0.55},
    },
    "SP": {
        "São Paulo":    {"populacao": 11451245, "pib_per_capita": 61290, "idh": 0.805, "gini": 0.58},
        "Campinas":     {"populacao": 1139534,  "pib_per_capita": 48320, "idh": 0.798, "gini": 0.52},
        "Ribeirão Preto": {"populacao": 698259, "pib_per_capita": 45210, "idh": 0.800, "gini": 0.51},
    },
    "AM": {
        "Manaus":       {"populacao": 2063547, "pib_per_capita": 34580, "idh": 0.737, "gini": 0.56},
    },
    "PA": {
        "Belém":        {"populacao": 1303389, "pib_per_capita": 22870, "idh": 0.740, "gini": 0.58},
    },
    "RS": {
        "Porto Alegre": {"populacao": 1332570, "pib_per_capita": 45120, "idh": 0.782, "gini": 0.54},
    },
    "DF": {
        "Brasília":     {"populacao": 2817381, "pib_per_capita": 80778, "idh": 0.824, "gini": 0.52},
    },
    "RJ": {
        "Rio de Janeiro": {"populacao": 6211423, "pib_per_capita": 51330, "idh": 0.779, "gini": 0.60},
    },
    "PE": {
        "Recife":       {"populacao": 1488920, "pib_per_capita": 28360, "idh": 0.772, "gini": 0.62},
    },
    "CE": {
        "Fortaleza":    {"populacao": 2428678, "pib_per_capita": 25190, "idh": 0.764, "gini": 0.60},
    },
    "MG": {
        "Belo Horizonte": {"populacao": 2315560, "pib_per_capita": 39250, "idh": 0.793, "gini": 0.55},
    },
}


def dados_municipio(uf_sigla: str, nome_municipio: str) -> dict:
    """
    Retorna dados do município se disponível, senão dict vazio.
    """
    uf_data = DADOS_MUNICIPIO.get(uf_sigla.upper(), {})
    return uf_data.get(nome_municipio.title(), {})


# ─── Convenience functions ──────────────────────────────────────

async def dados_bioma(bioma: str) -> dict:
    return BIOMAS.get(bioma, {})


def dados_uf(uf_sigla: str) -> dict:
    return DADOS_UF.get(uf_sigla.upper(), {})


def calcular_idh_regiao(estados_siglas: list[str]) -> float:
    valores = [DADOS_UF[s].get("idh", 0) for s in estados_siglas if s in DADOS_UF]
    return round(sum(valores) / len(valores), 3) if valores else 0.7


def indicadores_compostos(uf_sigla: str, bioma: str, municipio: str = "") -> dict[str, Any]:
    """
    Retorna indicadores compostos para uma localidade.

    Composição do índice de vulnerabilidade (Camada 3 — documentação):
      vulnerabilidade = w1 * (1 - IDH_norm) + w2 * GINI + w3 * (1 - escolaridade_norm)
      onde:
        w1 = 0.40 (peso do IDH — capacidade institucional)
        w2 = 0.35 (peso da desigualdade — coesão social)
        w3 = 0.25 (peso da educação — capital humano)
        IDH_norm = IDH / 1.0 (escala 0-1)
        escolaridade_norm = escolaridade / 10 (assume máximo 10 anos)
      Faixa: 0 (mínima vulnerabilidade) a 1 (máxima vulnerabilidade)
    """
    uf = dados_uf(uf_sigla)
    bm = BIOMAS.get(bioma, {})

    # Resolução geográfica: municipal, uf_fallback ou uf
    mun = dados_municipio(uf_sigla, municipio)
    tem_municipio = bool(municipio)
    dados_sao_municipais = bool(mun)
    if tem_municipio and dados_sao_municipais:
        resolucao = "municipal"
    elif tem_municipio and not dados_sao_municipais:
        resolucao = "uf_fallback"
    else:
        resolucao = "uf"

    idh = mun.get("idh") if dados_sao_municipais else uf.get("idh", 0.7)
    gini = mun.get("gini") if dados_sao_municipais else uf.get("gini", 0.55)
    populacao = mun.get("populacao") if dados_sao_municipais else uf.get("populacao", 0)
    pib_pc = mun.get("pib_per_capita") if dados_sao_municipais else uf.get("pib_per_capita", 20000)
    escolaridade = uf.get("escolaridade", 7.0)
    expectativa_vida = uf.get("expectativa_vida", 74.0)
    area_uf_km2 = uf.get("area_km2", 0)

    # Índice de vulnerabilidade (documentado acima)
    v_idh = 0.40 * (1 - idh)
    v_gini = 0.35 * gini
    v_esc = 0.25 * (1 - min(escolaridade / 10, 1))
    vulnerabilidade = round(v_idh + v_gini + v_esc, 3)

    return {
        "_resolucao_geografica": resolucao,
        "idh": idh,
        "pib_per_capita": pib_pc,
        "populacao": populacao,
        "gini": gini,
        "escolaridade": escolaridade,
        "expectativa_vida": expectativa_vida,
        "area_uf_km2": area_uf_km2,
        "indice_vulnerabilidade": vulnerabilidade,
        "_composicao_vulnerabilidade": {
            "peso_idh": 0.40,
            "peso_gini": 0.35,
            "peso_escolaridade": 0.25,
            "parcela_idh": round(v_idh, 4),
            "parcela_gini": round(v_gini, 4),
            "parcela_escolaridade": round(v_esc, 4),
        },
        "estresse_hidrico": bm.get("estresse_hidrico", 0.5),
        "risco_incendio": bm.get("risco_incendio", 0.3),
        "cobertura_vegetal_pct": bm.get("cobertura_vegetal_pct", 50),
        "desmatamento_anual_km2": bm.get("desmatamento_anual_km2", 1000),
        "pib_agropecuaria_pct": bm.get("pib_agropecuaria_pct", 15),
    }


async def enriquecer_localizacao(localizacao: dict) -> dict:
    base = dict(localizacao)
    uf = base.get("estado", "")
    bioma = base.get("bioma", "")
    municipio = base.get("municipio", "")
    if bioma:
        base["dados_bioma"] = await dados_bioma(bioma)
    if uf:
        base["indicadores_uf"] = dados_uf(uf)
    if uf and bioma:
        comp = indicadores_compostos(uf, bioma, municipio)
        base["indicadores_compostos"] = comp
        base["_composicao_vulnerabilidade"] = comp.get("_composicao_vulnerabilidade", {})
        base["_resolucao_geografica"] = comp.get("_resolucao_geografica", "uf")
    return base
