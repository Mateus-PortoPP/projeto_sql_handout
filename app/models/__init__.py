from app.models.aluno import Aluno, AlunoCreate, AlunoPublic, AlunoUpdate
from app.models.reserva import (
    Reserva,
    ReservaCreate,
    ReservaPublic,
    ReservaUpdate,
    StatusReserva,
)
from app.models.viagem import (
    StatusViagem,
    Viagem,
    ViagemCreate,
    ViagemPublic,
    ViagemUpdate,
)

__all__ = [
    "Aluno",
    "AlunoCreate",
    "AlunoPublic",
    "AlunoUpdate",
    "Reserva",
    "ReservaCreate",
    "ReservaPublic",
    "ReservaUpdate",
    "StatusReserva",
    "StatusViagem",
    "Viagem",
    "ViagemCreate",
    "ViagemPublic",
    "ViagemUpdate",
]
