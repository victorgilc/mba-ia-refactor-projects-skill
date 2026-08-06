import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

# Configurar logging básico para registrar os erros detalhados no console
logging.basicConfig(level=logging.ERROR)

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Se for uma exceção HTTP padrão do Flask (como 404 ou 405), preserve-a!
        # Isso garante que rotas não encontradas retornem 404 e métodos errados retornem 405.
        if isinstance(e, HTTPException):
            return e

        # Logar o erro detalhado internamente no console do servidor
        logging.error("ERRO CRÍTICO CAPTURADO NO HANDLER GLOBAL: %s", str(e), exc_info=True)

        # Responder ao cliente com uma mensagem segura que não vaza detalhes internos ou caminhos
        return jsonify({
            "erro": "Ocorreu um erro interno no servidor",
            "detalhes": "Verifique os logs do servidor para mais informações"
        }), 500
