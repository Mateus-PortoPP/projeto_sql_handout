from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Aluno, AlunoCreate, AlunoPublic, AlunoUpdate

router = APIRouter(prefix="/alunos", tags=["Alunos"])

AlunoId = Annotated[int, Path(description="ID do aluno", examples=[1])]

RESPOSTA_404 = {404: {"description": "Aluno não encontrado"}}
RESPOSTA_409 = {409: {"description": "E-mail ou matrícula já cadastrados"}}


def buscar_aluno(session: SessionDep, aluno_id: int) -> Aluno:
    aluno = session.get(Aluno, aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


def salvar_aluno(session: SessionDep, aluno: Aluno) -> Aluno:
    session.add(aluno)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="E-mail ou matrícula já cadastrados"
        )
    session.refresh(aluno)
    return aluno


@router.post(
    "",
    response_model=AlunoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar aluno",
    description="Cadastra um novo aluno. E-mail e matrícula devem ser únicos.",
    responses=RESPOSTA_409,
)
def criar_aluno(aluno: AlunoCreate, session: SessionDep):
    return salvar_aluno(session, Aluno.model_validate(aluno))


@router.get(
    "",
    response_model=list[AlunoPublic],
    summary="Listar alunos",
    description="Lista os alunos cadastrados, com paginação e filtro opcional por curso.",
)
def listar_alunos(
    session: SessionDep,
    curso: Annotated[
        str | None,
        Query(description="Filtra pelo curso", examples=["Ciência da Computação"]),
    ] = None,
    offset: Annotated[int, Query(ge=0, description="Quantos registros pular")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Máximo de registros retornados")
    ] = 20,
):
    consulta = select(Aluno)
    if curso:
        consulta = consulta.where(Aluno.curso == curso)
    return session.exec(consulta.offset(offset).limit(limit)).all()


@router.get(
    "/{aluno_id}",
    response_model=AlunoPublic,
    summary="Consultar aluno",
    description="Retorna os dados de um aluno pelo ID.",
    responses=RESPOSTA_404,
)
def obter_aluno(aluno_id: AlunoId, session: SessionDep):
    return buscar_aluno(session, aluno_id)


@router.patch(
    "/{aluno_id}",
    response_model=AlunoPublic,
    summary="Atualizar aluno",
    description="Atualiza apenas os campos enviados no corpo da requisição.",
    responses={**RESPOSTA_404, **RESPOSTA_409},
)
def atualizar_aluno(aluno_id: AlunoId, dados: AlunoUpdate, session: SessionDep):
    aluno = buscar_aluno(session, aluno_id)
    aluno.sqlmodel_update(dados.model_dump(exclude_unset=True, exclude_none=True))
    return salvar_aluno(session, aluno)


@router.delete(
    "/{aluno_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover aluno",
    description="Remove um aluno. As viagens e reservas dele também são removidas.",
    responses=RESPOSTA_404,
)
def remover_aluno(aluno_id: AlunoId, session: SessionDep):
    aluno = buscar_aluno(session, aluno_id)
    session.delete(aluno)
    session.commit()
