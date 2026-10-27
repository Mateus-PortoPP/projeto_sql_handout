from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import NaiveDatetime, field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.reserva import Reserva


class StatusViagem(str, Enum):
    agendada = "agendada"
    em_andamento = "em_andamento"
    concluida = "concluida"
    cancelada = "cancelada"


def remover_fuso(valor):
    """Aceita datas com fuso horário convertendo-as para o horário local sem fuso,
    já que a coluna DATETIME do MySQL não armazena fuso."""
    if isinstance(valor, str):
        try:
            valor = datetime.fromisoformat(valor)
        except ValueError:
            return valor
    if isinstance(valor, datetime) and valor.tzinfo is not None:
        return valor.astimezone().replace(tzinfo=None)
    return valor


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

    _validar_data = field_validator("data_hora_partida", mode="before")(remover_fuso)


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
    origem: str | None = Field(
        default=None,
        max_length=150,
        description="Novo ponto de partida",
        schema_extra={"examples": ["Estação Pinheiros"]},
    )
    destino: str | None = Field(
        default=None,
        max_length=150,
        description="Novo ponto de chegada",
        schema_extra={"examples": ["Campus Central - Av. Exemplo, 1000"]},
    )
    data_hora_partida: NaiveDatetime | None = Field(
        default=None,
        description="Nova data e hora de partida",
        schema_extra={"examples": ["2026-10-20T08:00:00"]},
    )
    vagas_totais: int | None = Field(
        default=None,
        ge=1,
        le=6,
        description="Nova quantidade de vagas",
        schema_extra={"examples": [4]},
    )
    preco_por_pessoa: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=6,
        decimal_places=2,
        description="Novo valor por passageiro (R$)",
        schema_extra={"examples": ["10.00"]},
    )
    status: StatusViagem | None = Field(
        default=None,
        description="Novo status da viagem",
        schema_extra={"examples": ["em_andamento"]},
    )

    _validar_data = field_validator("data_hora_partida", mode="before")(remover_fuso)


class ViagemPublic(ViagemBase):
    id: int
    motorista_id: int
    status: StatusViagem
