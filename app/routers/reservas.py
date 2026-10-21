from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Aluno,
    Reserva,
    ReservaCreate,
    ReservaPublic,
    ReservaUpdate,
    StatusReserva,
    Viagem,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

ReservaId = Annotated[int, Path(description="ID da reserva", examples=[1])]

RESPOSTA_404 = {404: {"description": "Reserva não encontrada"}}


def buscar_reserva(session: SessionDep, reserva_id: int) -> Reserva:
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reserva


@router.post(
    "",
    response_model=ReservaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Reservar vaga",
    description="Reserva uma vaga para um aluno (passageiro) em uma viagem. "
    "A reserva começa com status `confirmada`.",
    responses={
        404: {"description": "Viagem ou passageiro não encontrado"},
        409: {"description": "O aluno já possui reserva nesta viagem"},
    },
)
def criar_reserva(reserva: ReservaCreate, session: SessionDep):
    if not session.get(Viagem, reserva.viagem_id):
        raise HTTPException(status_code=404, detail="Viagem não encontrada")
    if not session.get(Aluno, reserva.passageiro_id):
        raise HTTPException(status_code=404, detail="Passageiro não encontrado")
    db_reserva = Reserva.model_validate(reserva)
    session.add(db_reserva)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="O aluno já possui reserva nesta viagem"
        )
    session.refresh(db_reserva)
    return db_reserva


@router.get(
    "",
    response_model=list[ReservaPublic],
    summary="Listar reservas",
    description="Lista as reservas, com paginação e filtros opcionais por viagem, "
    "passageiro e status.",
)
def listar_reservas(
    session: SessionDep,
    viagem_id: Annotated[
        int | None, Query(description="Filtra pelo ID da viagem", examples=[1])
    ] = None,
    passageiro_id: Annotated[
        int | None, Query(description="Filtra pelo ID do passageiro", examples=[2])
    ] = None,
    status_reserva: Annotated[
        StatusReserva | None,
        Query(alias="status", description="Filtra pelo status da reserva"),
    ] = None,
    offset: Annotated[int, Query(ge=0, description="Quantos registros pular")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Máximo de registros retornados")
    ] = 20,
):
    consulta = select(Reserva)
    if viagem_id is not None:
        consulta = consulta.where(Reserva.viagem_id == viagem_id)
    if passageiro_id is not None:
        consulta = consulta.where(Reserva.passageiro_id == passageiro_id)
    if status_reserva:
        consulta = consulta.where(Reserva.status == status_reserva)
    return session.exec(consulta.offset(offset).limit(limit)).all()


@router.get(
    "/{reserva_id}",
    response_model=ReservaPublic,
    summary="Consultar reserva",
    description="Retorna os dados de uma reserva pelo ID.",
    responses=RESPOSTA_404,
)
def obter_reserva(reserva_id: ReservaId, session: SessionDep):
    return buscar_reserva(session, reserva_id)


@router.patch(
    "/{reserva_id}",
    response_model=ReservaPublic,
    summary="Atualizar status da reserva",
    description="Altera o status da reserva (por exemplo, para `cancelada`).",
    responses=RESPOSTA_404,
)
def atualizar_reserva(
    reserva_id: ReservaId, dados: ReservaUpdate, session: SessionDep
):
    reserva = buscar_reserva(session, reserva_id)
    reserva.sqlmodel_update(dados.model_dump(exclude_unset=True, exclude_none=True))
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    return reserva


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover reserva",
    description="Remove uma reserva.",
    responses=RESPOSTA_404,
)
def remover_reserva(reserva_id: ReservaId, session: SessionDep):
    reserva = buscar_reserva(session, reserva_id)
    session.delete(reserva)
    session.commit()
