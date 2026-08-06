from flask import Flask
from flask_cors import CORS
from src.config import settings
from src.models import database
from src.views.routes import setup_routes
from src.middlewares.error_handler import register_error_handlers

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
CORS(app)

# Inicializar banco de dados de forma limpa no ciclo de vida do Flask
database.init_db(app)

# Registrar tratamento de exceções global e tratamento correto de HTTPExceptions
register_error_handlers(app)

# Configurar roteamento completo mapeando URLs para controllers
setup_routes(app)

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR REESTRUTURADO INICIADO (PADRÃO MVC)")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
