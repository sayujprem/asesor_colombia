import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def get_env(key: str, default: str | None = None, required: bool = True) -> str:
    value = os.getenv(key, default)
    if required and value is None:
        print(f"\n[ERROR] Variable de entorno requerida no encontrada: {key}")
        print(f"        Añade '{key}=tu-valor' a tu archivo .env en la carpeta 'asesor/'")
        sys.exit(1)
    return value


ANTHROPIC_API_KEY = get_env("ANTHROPIC_API_KEY")
MODEL = get_env("CLAUDE_MODEL", default="claude-sonnet-4-6", required=False)
MAX_TOKENS = int(get_env("MAX_TOKENS", default="4096", required=False))
UVT_VIGENTE = float(get_env("UVT_VIGENTE", default="52669", required=False))
SMLMV_VIGENTE = float(get_env("SMLMV_VIGENTE", default="1750905", required=False))
