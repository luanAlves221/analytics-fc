import os
from dotenv import load_dotenv

load_dotenv()

def _validar_ambiente():
    """Falha cedo com erro claro quando variáveis obrigatórias estão ausentes."""
    ausentes = [var for var in ("SECRET_KEY",) if not os.getenv(var)]
    if ausentes:
        raise RuntimeError(
            "Variáveis de ambiente ausentes: "
            + ", ".join(ausentes)
            + ". Copie o .env.example para .env e preencha os valores."
        )

_validar_ambiente()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
