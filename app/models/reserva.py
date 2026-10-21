from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.aluno import Aluno
    from app.models.viagem import Viagem


class StatusReserva(str, Enum):
    confirmada = "confirmada"
    cancelada = "cancelada"


class ReservaBase(SQLModel):
    viagem_id: int = Field(
        foreign_key="viagem.id",
        ondelete="CASCADE",
        description="ID da viagem reservada",
        schema_extra={"examples": [1]},
    )
    passageiro_id: int = Field(
        foreign_key="aluno.id",
        ondelete="CASCADE",
        description="ID do aluno que vai de carona",
        schema_extra={"examples": [2]},
    )


class Reserva(ReservaBase, table=True):
    __table_args__ = (
        UniqueConstraint("viagem_id", "passageiro_id", name="uq_reserva_viagem_passageiro"),
    )

    id: int | None = Field(default=None, primary_key=True)
    status: StatusReserva = Field(default=StatusReserva.confirmada)
    criada_em: NaiveDatetime = Field(default_factory=datetime.now)

    viagem: "Viagem" = Relationship(back_populates="reservas")
    passageiro: "Aluno" = Relationship(back_populates="reservas")


class ReservaCreate(ReservaBase):
    pass


class ReservaUpdate(SQLModel):
    status: StatusReserva | None = Field(
        default=None,
        description="Novo status da reserva",
        schema_extra={"examples": ["cancelada"]},
    )


class ReservaPublic(ReservaBase):
    id: int
    status: StatusReserva
    criada_em: NaiveDatetime
