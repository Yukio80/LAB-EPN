from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PropostaStatus(str, Enum):
    rascunho = "rascunho"
    em_validacao = "em_validacao"
    em_simulacao = "em_simulacao"
    simulacao_concluida = "simulacao_concluida"
    em_votacao = "em_votacao"
    aprovada = "aprovada"
    rejeitada = "rejeitada"
    em_execucao = "em_execucao"
    concluida = "concluida"
    arquivada = "arquivada"


class PropostaORM(Base):
    __tablename__ = "propostas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    versao: Mapped[int] = mapped_column(Integer, default=1)
    titulo: Mapped[str] = mapped_column(String(200))
    resumo: Mapped[str] = mapped_column(String(1000))
    descricao: Mapped[str] = mapped_column(Text)
    problema: Mapped[str] = mapped_column(Text)
    solucao: Mapped[str] = mapped_column(Text)
    orcamento_estimado: Mapped[float] = mapped_column(Float)
    moeda: Mapped[str] = mapped_column(String(10), default="BRL")
    autor_id: Mapped[str] = mapped_column(String(100))
    autor_tipo: Mapped[str] = mapped_column(String(50))
    organizacao: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    localizacao: Mapped[dict] = mapped_column(JSON)
    ods_vinculados: Mapped[list] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), default="rascunho")
    hash_credential: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    zero_knowledge_proof: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    simulacao: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    resultado_votacao: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    contrato_endereco: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(String(30))
    updated_at: Mapped[str] = mapped_column(String(30))
    published_at: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    tags: Mapped[list] = mapped_column(JSON)


class Localizacao(BaseModel):
    regiao: str
    estado: str
    municipio: Optional[str] = None
    bioma: Optional[str] = None


class SimulacaoResultado(BaseModel):
    id_simulacao: str
    motor_utilizado: str
    metricas: dict
    contexto_regional: dict = Field(default_factory=dict)
    relatorio_hash_ipfs: Optional[str] = None
    timestamp: str


class PropostaInput(BaseModel):
    titulo: str = Field(..., min_length=10, max_length=200)
    resumo: str = Field(..., min_length=50, max_length=1000)
    descricao: str = Field(..., min_length=100)
    problema: str
    solucao: str
    orcamento_estimado: float = Field(..., gt=0)
    moeda: str = "BRL"
    autor_id: str
    autor_tipo: str
    organizacao: Optional[str] = None
    localizacao: Localizacao
    ods_vinculados: list[int] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PropostaResponse(BaseModel):
    id: str
    versao: int
    titulo: str
    resumo: str
    descricao: str
    problema: str
    solucao: str
    orcamento_estimado: float
    moeda: str
    autor_id: str
    autor_tipo: str
    organizacao: Optional[str]
    localizacao: Localizacao
    ods_vinculados: list[int]
    status: PropostaStatus
    simulacao: Optional[SimulacaoResultado]
    resultado_votacao: Optional[dict]
    contrato_endereco: Optional[str]
    created_at: str
    updated_at: str
    published_at: Optional[str]
    tags: list[str]

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(obj: PropostaORM) -> "PropostaResponse":
        return PropostaResponse(
            id=obj.id,
            versao=obj.versao,
            titulo=obj.titulo,
            resumo=obj.resumo,
            descricao=obj.descricao,
            problema=obj.problema,
            solucao=obj.solucao,
            orcamento_estimado=obj.orcamento_estimado,
            moeda=obj.moeda,
            autor_id=obj.autor_id,
            autor_tipo=obj.autor_tipo,
            organizacao=obj.organizacao,
            localizacao=Localizacao(**obj.localizacao),
            ods_vinculados=obj.ods_vinculados,
            status=PropostaStatus(obj.status),
            simulacao=SimulacaoResultado(**obj.simulacao) if obj.simulacao else None,
            resultado_votacao=obj.resultado_votacao,
            contrato_endereco=obj.contrato_endereco,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            published_at=obj.published_at,
            tags=obj.tags,
        )
