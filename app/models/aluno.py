from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr, NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.reserva import Reserva
    from app.models.viagem import Viagem


class AlunoBase(SQLModel):
    nome: str = Field(
        max_length=100,
        description="Nome completo do aluno",
        schema_extra={"examples": ["Maria Souza"]},
    )
    email: EmailStr = Field(
        max_length=120,
        unique=True,
        description="E-mail institucional do aluno",
        schema_extra={"examples": ["maria.souza@exemplo.com"]},
    )
    matricula: str = Field(
        max_length=20,
        unique=True,
        description="Número de matrícula na faculdade",
        schema_extra={"examples": ["2023001234"]},
    )
    curso: str = Field(
        max_length=60,
        description="Curso do aluno",
        schema_extra={"examples": ["Ciência da Computação"]},
    )
    possui_carro: bool = Field(
        default=False,
        description="Indica se o aluno possui carro",
        schema_extra={"examples": [True]},
    )


class Aluno(AlunoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data_cadastro: NaiveDatetime = Field(default_factory=datetime.now)

    viagens_como_motorista: list["Viagem"] = Relationship(
        back_populates="motorista", cascade_delete=True
    )
    reservas: list["Reserva"] = Relationship(
        back_populates="passageiro", cascade_delete=True
    )


class AlunoCreate(AlunoBase):
    pass


class AlunoUpdate(SQLModel):
    nome: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=120)
    matricula: str | None = Field(default=None, max_length=20)
    curso: str | None = Field(default=None, max_length=60)
    possui_carro: bool | None = None


class AlunoPublic(AlunoBase):
    id: int
    data_cadastro: NaiveDatetime
