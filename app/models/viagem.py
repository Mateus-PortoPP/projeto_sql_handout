from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.reserva import Reserva


class StatusViagem(str, Enum):
    agendada = "agendada"
    em_andamento = "em_andamento"
    concluida = "concluida"
    cancelada = "cancelada"


class ViagemBase(SQLModel):
    origem: str = Field(
        max_length=150,
        description="Ponto de partida da viagem",
        schema_extra={"examples": ["Estação Faria Lima"]},
    )
    destino: str = Field(
        max_length=150,
        description="Ponto de chegada da viagem",
        schema_extra={"examples": ["Campus Central - Av. Exemplo, 1000"]},
    )
    data_hora_partida: NaiveDatetime = Field(
        description="Data e hora previstas de partida",
        schema_extra={"examples": ["2026-10-20T07:30:00"]},
    )
    vagas_totais: int = Field(
        ge=1,
        le=6,
        description="Quantidade de vagas oferecidas para passageiros",
        schema_extra={"examples": [3]},
    )
    preco_por_pessoa: Decimal = Field(
        ge=0,
        max_digits=6,
        decimal_places=2,
        description="Valor cobrado de cada passageiro (R$)",
        schema_extra={"examples": ["8.50"]},
    )


class Viagem(ViagemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    motorista_id: int = Field(foreign_key="aluno.id", ondelete="CASCADE")
    status: StatusViagem = Field(default=StatusViagem.agendada)

    motorista: "Aluno" = Relationship(back_populates="viagens_como_motorista")
    reservas: list["Reserva"] = Relationship(
        back_populates="viagem", cascade_delete=True
    )


class ViagemCreate(ViagemBase):
    motorista_id: int = Field(
        description="ID do aluno que vai dirigir",
        schema_extra={"examples": [1]},
    )


class ViagemUpdate(SQLModel):
    origem: str | None = Field(default=None, max_length=150)
    destino: str | None = Field(default=None, max_length=150)
    data_hora_partida: NaiveDatetime | None = None
    vagas_totais: int | None = Field(default=None, ge=1, le=6)
    preco_por_pessoa: Decimal | None = Field(
        default=None, ge=0, max_digits=6, decimal_places=2
    )
    status: StatusViagem | None = None


class ViagemPublic(ViagemBase):
    id: int
    motorista_id: int
    status: StatusViagem
