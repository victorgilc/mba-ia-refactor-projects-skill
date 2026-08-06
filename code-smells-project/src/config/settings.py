import os

SECRET_KEY = os.environ.get("SECRET_KEY", "minha-chave-super-secreta-123")
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
