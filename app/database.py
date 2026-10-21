from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def create_db_and_tables() -> None:
    # Importa os modelos para registrá-los no metadata antes do create_all
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
