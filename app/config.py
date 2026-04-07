from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def _clean(value: str | None, default: str = "") -> str:
    if value is None:
        return default
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()

APP_NAME = "Homie"
APP_VERSION = "3.1.0-fixed"

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

DASHSCOPE_API_KEY = _clean(os.getenv("DASHSCOPE_API_KEY", ""))
OPENAI_API_KEY = _clean(os.getenv("OPENAI_API_KEY", DASHSCOPE_API_KEY or ""))
OPENAI_BASE_URL = _clean(
    os.getenv("OPENAI_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
).rstrip("/")
OPENAI_MODEL = _clean(os.getenv("OPENAI_MODEL", "qwen3-max"))

LOGS_PASSWORD = _clean(os.getenv("LOGS_PASSWORD", "123456"))
LLM_TIMEOUT_SECONDS = float(_clean(os.getenv("LLM_TIMEOUT_SECONDS", "30"), "30"))
