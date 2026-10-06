import os
import secrets
from dotenv import load_dotenv

load_dotenv()

CAMINHO_SECRET_KEY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "instance",
    "secret_key",
)

def _obter_secret_key():
    """Usa o valor do ambiente ou gera/persiste uma chave local estável."""
    chave = os.getenv("SECRET_KEY")
    if chave:
        return chave
    if os.path.exists(CAMINHO_SECRET_KEY):
        with open(CAMINHO_SECRET_KEY, encoding="utf-8") as arquivo:
            return arquivo.read().strip()
    chave_gerada = secrets.token_hex(32)
    os.makedirs(os.path.dirname(CAMINHO_SECRET_KEY), exist_ok=True)
    with open(CAMINHO_SECRET_KEY, "w", encoding="utf-8") as arquivo:
        arquivo.write(chave_gerada)
    return chave_gerada

class Config:
    SECRET_KEY = _obter_secret_key()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
