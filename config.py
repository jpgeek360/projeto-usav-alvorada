import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-alterar-em-producao")
    DATA_FILE = BASE_DIR / "data" / "banco.json"
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ITEMS_PER_PAGE = 20  # Grid 4 colunas x 5 linhas
    WHATSAPP_ADOCAO_PADRAO = "5551999990000"