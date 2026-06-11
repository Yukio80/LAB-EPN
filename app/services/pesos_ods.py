"""
Tabela de Pesos dos ODS — v1.0

Cada ODS tem coeficientes que modulam o impacto da proposta nas 5 métricas.
Os pesos foram calibrados com base em:
  - Metas oficiais dos ODS (ONU/IPEA)
  - Correlações históricas entre investimento setorial e indicadores (IBGE/PNAD)
  - Revisão por pares (pendente: Comitê de Validação)

Versionamento:
  - v1.0: calibração inicial do desenvolvedor
  - Próxima versão: após primeira rodada do Comitê de Validação

Formato por ODS:
  {ods_id: {
    "nome": "...",
    "meta_resumo": "...",
    "pesos": {
      "desigualdade": float,   # impacto na redução da desigualdade (negativo = reduz)
      "emprego": float,        # impacto na geração de emprego
      "confianca": float,      # impacto na confiança social
      "conflito": float,       # impacto na redução de conflitos (negativo = reduz)
      "pib": float,            # impacto no PIB per capita
      "sinergia_titulo": [str], # palavras-chave que amplificam o efeito
      "sinergia_contexto": {str: float},  # contextos que amplificam (ex: "estresse_hidrico>0.6": 1.5x)
    }
  }}
"""

PESOS_ODS: dict[int, dict] = {
    1: {
        "nome": "Erradicação da Pobreza",
        "meta_resumo": "Acabar com a pobreza em todas as suas formas, em todos os lugares",
        "pesos": {
            "desigualdade": -0.12,
            "emprego": 0.08,
            "confianca": 0.06,
            "conflito": -0.06,
            "pib": 0.03,
            "sinergia_titulo": ["pobreza", "renda", "bolsa", "transferencia"],
            "sinergia_contexto": {"gini>0.56": 1.3},
        },
    },
    2: {
        "nome": "Fome Zero e Agricultura Sustentável",
        "meta_resumo": "Acabar com a fome, alcançar a segurança alimentar e promover agricultura sustentável",
        "pesos": {
            "desigualdade": -0.06,
            "emprego": 0.12,
            "confianca": 0.05,
            "conflito": -0.04,
            "pib": 0.05,
            "sinergia_titulo": ["fome", "agricultura", "alimento", "seguranca alimentar"],
            "sinergia_contexto": {"pib_agropecuaria_pct>20": 1.4},
        },
    },
    3: {
        "nome": "Saúde e Bem-Estar",
        "meta_resumo": "Assegurar vida saudável e promover bem-estar para todos",
        "pesos": {
            "desigualdade": -0.05,
            "emprego": 0.04,
            "confianca": 0.10,
            "conflito": -0.03,
            "pib": 0.02,
            "sinergia_titulo": ["saude", "hospital", "vacina", "sus", "bem-estar"],
            "sinergia_contexto": {"expectativa_vida<73": 1.2},
        },
    },
    4: {
        "nome": "Educação de Qualidade",
        "meta_resumo": "Assegurar educação inclusiva, equitativa e de qualidade para todos",
        "pesos": {
            "desigualdade": -0.10,
            "emprego": 0.07,
            "confianca": 0.12,
            "conflito": -0.05,
            "pib": 0.04,
            "sinergia_titulo": ["educacao", "escola", "professor", "universidade"],
            "sinergia_contexto": {"escolaridade<7": 1.3},
        },
    },
    5: {
        "nome": "Igualdade de Gênero",
        "meta_resumo": "Alcançar igualdade de gênero e empoderar mulheres e meninas",
        "pesos": {
            "desigualdade": -0.08,
            "emprego": 0.06,
            "confianca": 0.08,
            "conflito": -0.04,
            "pib": 0.03,
            "sinergia_titulo": ["genero", "mulher", "feminino", "igualdade"],
            "sinergia_contexto": {"gini>0.55": 1.2},
        },
    },
    6: {
        "nome": "Água Potável e Saneamento",
        "meta_resumo": "Garantir disponibilidade e gestão sustentável de água e saneamento",
        "pesos": {
            "desigualdade": -0.07,
            "emprego": 0.06,
            "confianca": 0.10,
            "conflito": -0.10,
            "pib": 0.04,
            "sinergia_titulo": ["agua", "saneamento", "esgoto", "bacia", "rio"],
            "sinergia_contexto": {"estresse_hidrico>0.6": 1.5},
        },
    },
    7: {
        "nome": "Energia Limpa e Acessível",
        "meta_resumo": "Garantir acesso a energia limpa, confiável e moderna para todos",
        "pesos": {
            "desigualdade": -0.04,
            "emprego": 0.06,
            "confianca": 0.04,
            "conflito": -0.02,
            "pib": 0.06,
            "sinergia_titulo": ["energia", "solar", "eolica", "renovavel"],
            "sinergia_contexto": {},
        },
    },
    8: {
        "nome": "Trabalho Decente e Crescimento Econômico",
        "meta_resumo": "Promover crescimento econômico inclusivo, emprego pleno e trabalho decente",
        "pesos": {
            "desigualdade": -0.06,
            "emprego": 0.18,
            "confianca": 0.06,
            "conflito": -0.05,
            "pib": 0.08,
            "sinergia_titulo": ["emprego", "trabalho", "renda", "formacao profissional"],
            "sinergia_contexto": {"escolaridade<7": 1.2},
        },
    },
    9: {
        "nome": "Indústria, Inovação e Infraestrutura",
        "meta_resumo": "Construir infraestrutura resiliente, promover industrialização inclusiva e fomentar inovação",
        "pesos": {
            "desigualdade": -0.03,
            "emprego": 0.10,
            "confianca": 0.04,
            "conflito": -0.02,
            "pib": 0.10,
            "sinergia_titulo": ["infraestrutura", "industria", "inovacao", "rodovia", "porto"],
            "sinergia_contexto": {},
        },
    },
    10: {
        "nome": "Redução das Desigualdades",
        "meta_resumo": "Reduzir desigualdades dentro dos países e entre eles",
        "pesos": {
            "desigualdade": -0.20,
            "emprego": 0.06,
            "confianca": 0.08,
            "conflito": -0.08,
            "pib": 0.02,
            "sinergia_titulo": ["desigualdade", "inclusao", "acessibilidade"],
            "sinergia_contexto": {"gini>0.56": 1.4},
        },
    },
    11: {
        "nome": "Cidades e Comunidades Sustentáveis",
        "meta_resumo": "Tornar cidades e assentamentos humanos inclusivos, seguros e sustentáveis",
        "pesos": {
            "desigualdade": -0.05,
            "emprego": 0.06,
            "confianca": 0.07,
            "conflito": -0.06,
            "pib": 0.04,
            "sinergia_titulo": ["cidade", "urbano", "mobilidade", "habitacao"],
            "sinergia_contexto": {},
        },
    },
    12: {
        "nome": "Consumo e Produção Responsáveis",
        "meta_resumo": "Assegurar padrões de consumo e produção sustentáveis",
        "pesos": {
            "desigualdade": -0.03,
            "emprego": 0.04,
            "confianca": 0.05,
            "conflito": -0.03,
            "pib": 0.03,
            "sinergia_titulo": ["consumo", "producao", "sustentavel", "reciclagem"],
            "sinergia_contexto": {},
        },
    },
    13: {
        "nome": "Ação Contra a Mudança Climática",
        "meta_resumo": "Adotar medidas urgentes para combater mudanças climáticas e seus impactos",
        "pesos": {
            "desigualdade": -0.04,
            "emprego": 0.05,
            "confianca": 0.07,
            "conflito": -0.06,
            "pib": 0.03,
            "sinergia_titulo": ["clima", "mudanca climatica", "carbono", "emissoes"],
            "sinergia_contexto": {"risco_incendio>0.5": 1.3, "cobertura_vegetal_pct<30": 1.2},
        },
    },
    14: {
        "nome": "Vida na Água",
        "meta_resumo": "Conservar e usar sustentavelmente oceanos, mares e recursos marinhos",
        "pesos": {
            "desigualdade": -0.03,
            "emprego": 0.04,
            "confianca": 0.05,
            "conflito": -0.04,
            "pib": 0.02,
            "sinergia_titulo": ["oceano", "mar", "costeiro", "pesca"],
            "sinergia_contexto": {},
        },
    },
    15: {
        "nome": "Vida Terrestre",
        "meta_resumo": "Proteger, restaurar e promover uso sustentável de ecossistemas terrestres",
        "pesos": {
            "desigualdade": -0.04,
            "emprego": 0.06,
            "confianca": 0.06,
            "conflito": -0.05,
            "pib": 0.03,
            "sinergia_titulo": ["floresta", "reflorestamento", "biodiversidade", "mata"],
            "sinergia_contexto": {"cobertura_vegetal_pct<40": 1.3, "desmatamento_anual_km2>1000": 1.2},
        },
    },
    16: {
        "nome": "Paz, Justiça e Instituições Eficazes",
        "meta_resumo": "Promover sociedades pacíficas e inclusivas, acesso à justiça e instituições responsáveis",
        "pesos": {
            "desigualdade": -0.06,
            "emprego": 0.03,
            "confianca": 0.15,
            "conflito": -0.15,
            "pib": 0.02,
            "sinergia_titulo": ["paz", "justica", "seguranca", "conselho", "participacao"],
            "sinergia_contexto": {"gini>0.56": 1.2},
        },
    },
    17: {
        "nome": "Parcerias e Meios de Implementação",
        "meta_resumo": "Fortalecer meios de implementação e revitalizar parceria global para o desenvolvimento",
        "pesos": {
            "desigualdade": -0.03,
            "emprego": 0.03,
            "confianca": 0.08,
            "conflito": -0.04,
            "pib": 0.02,
            "sinergia_titulo": ["parceria", "cooperacao", "integracao"],
            "sinergia_contexto": {},
        },
    },
}


def versao_pesos() -> str:
    return "1.0"


def obter_peso(ods_id: int, metrica: str, default: float = 0.0) -> float:
    entry = PESOS_ODS.get(ods_id)
    if not entry:
        return default
    return entry["pesos"].get(metrica, default)


def calcular_mult_contexto(ods_id: int, contexto: dict, titulo: str) -> float:
    entry = PESOS_ODS.get(ods_id)
    if not entry:
        return 1.0
    mult = 1.0
    for palavra in entry["pesos"].get("sinergia_titulo", []):
        if palavra in titulo.lower():
            mult *= 1.15
    for cond, fator in entry["pesos"].get("sinergia_contexto", {}).items():
        if ">" in cond:
            chave, limite = cond.rsplit(">", 1)
            if contexto.get(chave.strip(), 0) > float(limite):
                mult *= fator
        elif "<" in cond:
            chave, limite = cond.rsplit("<", 1)
            if contexto.get(chave.strip(), 1) < float(limite):
                mult *= fator
    return mult
