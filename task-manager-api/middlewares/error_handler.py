from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception(e)
        return jsonify({'error': 'Erro interno no servidor'}), 500
