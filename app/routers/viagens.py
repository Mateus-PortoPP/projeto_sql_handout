from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Aluno,
    StatusViagem,
    Viagem,
    ViagemCreate,
    ViagemPublic,
    ViagemUpdate,
)

router = APIRouter(prefix="/viagens", tags=["Viagens"])

ViagemId = Annotated[int, Path(description="ID da viagem", examples=[1])]

RESPOSTA_404 = {404: {"description": "Viagem não encontrada"}}


def buscar_viagem(session: SessionDep, viagem_id: int) -> Viagem:
    viagem = session.get(Viagem, viagem_id)
    if not viagem:
        raise HTTPException(status_code=404, detail="Viagem não encontrada")
    return viagem


@router.post(
    "",
    response_model=ViagemPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar viagem",
    description="Cadastra uma viagem oferecida por um aluno (motorista). "
    "A viagem começa com status `agendada`.",
    responses={404: {"description": "Motorista não encontrado"}},
)
def criar_viagem(viagem: ViagemCreate, session: SessionDep):
    if not session.get(Aluno, viagem.motorista_id):
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    db_viagem = Viagem.model_validate(viagem)
    session.add(db_viagem)
    session.commit()
    session.refresh(db_viagem)
    return db_viagem


@router.get(
    "",
    response_model=list[ViagemPublic],
    summary="Listar viagens",
    description="Lista as viagens, com paginação e filtros opcionais por status e motorista.",
)
def listar_viagens(
    session: SessionDep,
    status_viagem: Annotated[
        StatusViagem | None,
        Query(alias="status", description="Filtra pelo status da viagem"),
    ] = None,
    motorista_id: Annotated[
        int | None, Query(description="Filtra pelo ID do motorista", examples=[1])
    ] = None,
    offset: Annotated[int, Query(ge=0, description="Quantos registros pular")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Máximo de registros retornados")
    ] = 20,
):
    consulta = select(Viagem)
    if status_viagem:
        consulta = consulta.where(Viagem.status == status_viagem)
    if motorista_id is not None:
        consulta = consulta.where(Viagem.motorista_id == motorista_id)
    consulta = consulta.order_by(Viagem.data_hora_partida)
    return session.exec(consulta.offset(offset).limit(limit)).all()


@router.get(
    "/{viagem_id}",
    response_model=ViagemPublic,
    summary="Consultar viagem",
    description="Retorna os dados de uma viagem pelo ID.",
    responses=RESPOSTA_404,
)
def obter_viagem(viagem_id: ViagemId, session: SessionDep):
    return buscar_viagem(session, viagem_id)


@router.patch(
    "/{viagem_id}",
    response_model=ViagemPublic,
    summary="Atualizar viagem",
    description="Atualiza apenas os campos enviados, incluindo o status da viagem. "
    "O motorista não pode ser alterado.",
    responses=RESPOSTA_404,
)
def atualizar_viagem(viagem_id: ViagemId, dados: ViagemUpdate, session: SessionDep):
    viagem = buscar_viagem(session, viagem_id)
    viagem.sqlmodel_update(dados.model_dump(exclude_unset=True, exclude_none=True))
    session.add(viagem)
    session.commit()
    session.refresh(viagem)
    return viagem


@router.delete(
    "/{viagem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover viagem",
    description="Remove uma viagem. As reservas dela também são removidas.",
    responses=RESPOSTA_404,
)
def remover_viagem(viagem_id: ViagemId, session: SessionDep):
    viagem = buscar_viagem(session, viagem_id)
    session.delete(viagem)
    session.commit()
