from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import alunos, reservas, viagens


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Caronas Universitárias API",
    description="API REST para organizar caronas entre alunos da faculdade: "
    "alunos oferecem viagens como motoristas e reservam vagas como passageiros.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(alunos.router)
app.include_router(viagens.router)
app.include_router(reservas.router)
