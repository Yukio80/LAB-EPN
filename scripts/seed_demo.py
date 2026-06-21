"""
seed_demo.py — Popula o banco com 5 propostas de exemplo + simulacoes + votacao.

Uso:
    cd /root/LAB-EPN
    python scripts/seed_demo.py

Requisito: banco vazio (ou existente — ignora se propostas ja existirem).
"""
import asyncio
import hashlib
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///./lab-epn.db")
os.environ["OPENROUTER_API_KEY"] = ""  # força modo deterministico

from app.database import SessionLocal, engine, Base
from app.models.proposta import PropostaORM, PropostaStatus
from app.services.simulacao import SimulacaoRequest, chamar_motor_pangeia
from app.services.votacao_onchain import _votacoes, PropostaVotacao, _hash_proposta


PROPOSTAS = [
    {
        "titulo": "Saneamento Basico para Comunidades Rurais do Maranhao",
        "resumo": "Programa de implantacao de sistemas simplificados de agua e esgoto em 200 comunidades rurais maranhenses, com foco nos biomas Cerrado e Amazonia.",
        "descricao": "O Maranhao possui o menor indice de saneamento basico do Brasil, com apenas 34% da populacao atendida por rede de esgoto. Este programa propoe a implantacao de 200 sistemas simplificados de tratamento de agua e esgoto em comunidades rurais dos biomas Cerrado e Amazonia, beneficiando aproximadamente 80 mil pessoas. Cada sistema inclui fossa septica biodigestora, filtro de agua com membrana ceramica e capacitacao de moradores para manutencao.",
        "problema": "Apenas 34% da populacao maranhense tem acesso a rede de esgoto. Doencas de veiculacao hidrica como diarreia e hepatite A sao a segunda maior causa de internacao infantil no estado. A mortalidade infantil no Maranhao e 50% superior a media nacional.",
        "solucao": "Instalacao de 200 sistemas integrados de agua e saneamento em comunidades rurais, com tecnologia social de baixo custo (fossa biodigestora + filtro cerâmico). Capacitacao de 400 agentes comunitarios para operacao e manutencao. Monitoramento trimestral da qualidade da agua por 36 meses.",
        "orcamento_estimado": 45000000,
        "autor_id": "seed",
        "autor_tipo": "sistema",
        "organizacao": "LAB-EPN Demo",
        "localizacao": {
            "regiao": "Nordeste",
            "estado": "MA",
            "municipio": "Sao Luis",
            "bioma": "Cerrado",
        },
        "ods_vinculados": [6, 3],
        "tags": ["saneamento", "agua", "rural", "maranhao", "saude-publica"],
    },
    {
        "titulo": "Reflorestamento da Amazonia Paraense com Especies Nativas",
        "resumo": "Recuperacao de 50 mil hectares de areas degradadas no Para com especies nativas da Amazonia, gerando renda para comunidades extrativistas.",
        "descricao": "O Para e o estado com maior taxa de desmatamento da Amazonia brasileira. Este projeto propoe o reflorestamento de 50 mil hectares em 10 municipios paraenses com alto indice de desmatamento, utilizando especies nativas de alto valor economico como acai, castanha-do-para e mogno. O modelo inclui pagamento por servicos ambientais (PSA) para comunidades ribeirinhas e extrativistas que atuarem na manutencao das areas recuperadas.",
        "problema": "O Para perdeu 23% da cobertura vegetal original. O desmatamento anual medio e de 6.000 km2, gerando emissoes de CO2, perda de biodiversidade e desertificacao economica. Menos de 5% do desmatamento e recuperado ativamente.",
        "solucao": "Reflorestamento de 50 mil hectares com 30 especies nativas. Criacao de 3 viveiros comunitarios com capacidade de 2 milhoes de mudas/ano. Pagamento por servicos ambientais para 2.000 familias extrativistas. Monitoramento por satelite com alerta em tempo real.",
        "orcamento_estimado": 120000000,
        "autor_id": "seed",
        "autor_tipo": "sistema",
        "organizacao": "LAB-EPN Demo",
        "localizacao": {
            "regiao": "Norte",
            "estado": "PA",
            "municipio": "Belem",
            "bioma": "Amazonia",
        },
        "ods_vinculados": [13, 15],
        "tags": ["reflorestamento", "amazonia", "clima", "biodiversidade", "para"],
    },
    {
        "titulo": "Educacao Integral em Tempo Integral nas Escolas de Alagoas",
        "resumo": "Ampliacao da jornada escolar para tempo integral em 500 escolas da rede estadual de Alagoas, com foco em municipios de baixo IDH.",
        "descricao": "Alagoas tem o pior IDH educacional do Brasil, com taxa de abandono escolar de 12% no ensino medio e nota media de 4.2 no IDEB. Este programa propoe a ampliacao da jornada escolar para 7 horas diarias em 500 escolas estaduais, com currículo integrado que combina formacao academica, profissionalizante, cultural e esportiva. Inclui formacao continuada para professores e reforma de infraestrutura escolar.",
        "problema": "Alagoas registra 12% de abandono no ensino medio, contra 7% da media nacional. Apenas 18% das escolas estaduais oferecem tempo integral. O IDEB do estado e o menor do pais. A desigualdade educacional entre capital e interior e de 40% no desempenho em matematica.",
        "solucao": "Conversao de 500 escolas para tempo integral (7h/dia). Contratacao de 3.000 novos professores. Currículo integrado com trilhas profissionalizantes. Programa de permanencia escolar com bolsa-auxilio para alunos em vulnerabilidade. Reforma de infraestrutura com refeitorios, bibliotecas e quadras poliesportivas.",
        "orcamento_estimado": 850000000,
        "autor_id": "seed",
        "autor_tipo": "sistema",
        "organizacao": "LAB-EPN Demo",
        "localizacao": {
            "regiao": "Nordeste",
            "estado": "AL",
            "municipio": "Maceio",
            "bioma": "Mata Atlantica",
        },
        "ods_vinculados": [4, 10],
        "tags": ["educacao", "tempo-integral", "alagoas", "desigualdade"],
    },
    {
        "titulo": "Habitacao Popular Sustentavel na Periferia de Sao Paulo",
        "resumo": "Construcao de 15 mil unidades habitacionais populares com criterios de sustentabilidade em 15 distritos perifericos da capital paulista.",
        "descricao": "O deficit habitacional da Regiao Metropolitana de Sao Paulo e de 1.2 milhao de unidades. Este programa propoe a construcao de 15 mil moradias populares em 15 distritos perifericos, utilizando tecnicas de construcao sustentavel (painel solar, captacao de agua de chuva, tijolo ecologico). Cada unidade tera 52m2 com 2 quartos, sala, cozinha e banheiro. O programa inclui regularizacao fundiaria e acesso a linhas de credito subsidiado.",
        "problema": "Deficit habitacional de 1.2 milhao de unidades na RMSP. 30% da populacao da periferia vive em favelas ou assentamentos irregulares sem acesso a saneamento basico. O aluguel consome mais de 40% da renda de 60% das familias de baixa renda.",
        "solucao": "Construcao de 15 mil unidades com tecnologia sustentavel (painel fotovoltaico, reuso de agua, tijolo modular). Regularizacao fundiaria de 30 areas. Linha de credito com juro zero para familias com renda ate 3 salarios minimos. Criacao de 5 polos de servicos publicos integrados (saude, educacao, assistencia social).",
        "orcamento_estimado": 2500000000,
        "autor_id": "seed",
        "autor_tipo": "sistema",
        "organizacao": "LAB-EPN Demo",
        "localizacao": {
            "regiao": "Sudeste",
            "estado": "SP",
            "municipio": "Sao Paulo",
            "bioma": "Mata Atlantica",
        },
        "ods_vinculados": [11],
        "tags": ["habitacao", "sustentabilidade", "periferia", "sao-paulo"],
    },
    {
        "titulo": "Agricultura Familiar Resiliente no Semiarido Baiano",
        "resumo": "Fortalecimento da agricultura familiar no semiarido baiano com tecnicas agroecologicas e acesso a agua para irrigacao de baixo custo.",
        "descricao": "O semiarido baiano concentra 40% da populacao rural em situacao de pobreza extrema do estado. Este programa propoe a implantacao de 10 mil sistemas de irrigacao de baixo custo (gotejamento solar) em propriedades familiares, combinados com assistencia tecnica agroecologica, formacao de cooperativas e acesso a mercados institucionais (PNAE, PAA). A regiao e predominantemente de bioma Caatinga, com alta vulnerabilidade hidrica.",
        "problema": "A seca prolongada no semiarido baiano afeta 2 milhoes de pessoas. 60% das propriedades rurais sao de agricultura familiar e 70% nao tem acesso a irrigacao. A produtividade e 80% inferior a media nacional. A inseguranca alimentar atinge 45% das familias rurais da regiao.",
        "solucao": "Instalacao de 10 mil sistemas de irrigacao por gotejamento com bombeamento solar. Assistencia tecnica continuada para 15 mil agricultores. Formacao de 30 cooperativas de comercializacao. Acesso garantido ao PNAE e PAA para 100% da producao. Implantacao de 5 centros de beneficiamento e armazenamento de alimentos.",
        "orcamento_estimado": 180000000,
        "autor_id": "seed",
        "autor_tipo": "sistema",
        "organizacao": "LAB-EPN Demo",
        "localizacao": {
            "regiao": "Nordeste",
            "estado": "BA",
            "municipio": "Juazeiro",
            "bioma": "Caatinga",
        },
        "ods_vinculados": [2, 8],
        "tags": ["agricultura-familiar", "semiarido", "agroecologia", "bahia", "seca"],
    },
]

VOTACAO_IDS = {0, 1}


def _now():
    return datetime.now(timezone.utc).isoformat()


async def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existentes = db.query(PropostaORM).count()
    if existentes > 0:
        print(f"Banco ja tem {existentes} propostas. Pulando seed.")
        db.close()
        return

    criadas = []

    for idx, data in enumerate(PROPOSTAS):
        pid = str(uuid4())
        now = _now()
        orm = PropostaORM(
            id=pid,
            versao=1,
            titulo=data["titulo"],
            resumo=data["resumo"],
            descricao=data["descricao"],
            problema=data["problema"],
            solucao=data["solucao"],
            orcamento_estimado=data["orcamento_estimado"],
            moeda="BRL",
            autor_id=data["autor_id"],
            autor_tipo=data["autor_tipo"],
            organizacao=data["organizacao"],
            localizacao=data["localizacao"],
            ods_vinculados=data["ods_vinculados"],
            status=PropostaStatus.rascunho.value,
            simulacao=None,
            resultado_votacao=None,
            contrato_endereco=None,
            created_at=now,
            updated_at=now,
            published_at=None,
            tags=data["tags"],
        )
        db.add(orm)
        db.commit()
        print(f"[{idx+1}/5] Proposta criada: {data['titulo'][:60]}...")

        req = SimulacaoRequest(
            proposta_id=pid,
            titulo=data["titulo"],
            descricao=data["descricao"],
            problema=data["problema"],
            solucao=data["solucao"],
            orcamento=data["orcamento_estimado"],
            localizacao=data["localizacao"],
            ods=data["ods_vinculados"],
        )
        resultado = await chamar_motor_pangeia(req)

        orm.status = PropostaStatus.simulacao_concluida.value
        orm.simulacao = {
            "id_simulacao": str(resultado.id_simulacao),
            "motor_utilizado": resultado.motor_usado,
            "modelo_versao": resultado.modelo_versao,
            "pesos_ods_versao": resultado.pesos_ods_versao,
            "metricas": resultado.metricas,
            "contexto_regional": resultado.contexto_regional,
            "metodologia": resultado.metodologia,
            "relatorio_hash_ipfs": resultado.hash_ipfs,
            "timestamp": _now(),
        }
        orm.updated_at = _now()
        db.commit()
        print(f"  -> Simulacao concluida (motor: {resultado.motor_usado})")

        if idx in VOTACAO_IDS:
            now_pub = _now()
            orm.status = PropostaStatus.em_votacao.value
            orm.published_at = now_pub
            orm.updated_at = now_pub

            hash_prop = _hash_proposta(data["titulo"], data["descricao"], data["orcamento_estimado"])
            voto_pid = str(uuid4())
            contrato_addr = "0x" + hashlib.sha256(f"contract_{voto_pid}".encode()).hexdigest()[:40]

            orm.contrato_endereco = contrato_addr
            orm.resultado_votacao = {
                "votos_sim": 0, "votos_nao": 0,
                "creditos_sim": 0, "creditos_nao": 0,
            }
            if orm.simulacao:
                orm.simulacao["contrato"] = {
                    "contrato_endereco": contrato_addr,
                    "proposta_id": voto_pid,
                    "hash_proposta": hash_prop,
                    "deadline": now_pub,
                    "network": "simulacao_local",
                }

            _votacoes[pid] = PropostaVotacao(
                id=pid,
                titulo=data["titulo"],
                hash_proposta=hash_prop,
                ativa=True,
                criada_em=now_pub,
                deadline=now_pub,
            )
            db.commit()
            print(f"  -> Publicada em votacao on-chain (contrato: {contrato_addr[:16]}...)")

        criadas.append(pid)

    db.close()

    print(f"\nSeed concluido! {len(criadas)} propostas criadas, simuladas e disponiveis.")
    print(f"  {len(VOTACAO_IDS)} em votacao on-chain.")
    print("Para resetar: rm lab-epn.db && python scripts/seed_demo.py")


if __name__ == "__main__":
    asyncio.run(seed())
