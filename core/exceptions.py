# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Exceptions
Tratamento centralizado de erros e exceções
"""

from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

class SemapaException(Exception):
    """Exceção base do sistema SEMAPA"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(SemapaException):
    """Erro de validação de dados"""
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(message, 400)

class NotFoundError(SemapaException):
    """Recurso não encontrado"""
    def __init__(self, message="Recurso não encontrado"):
        super().__init__(message, 404)

class UnauthorizedError(SemapaException):
    """Acesso não autorizado"""
    def __init__(self, message="Acesso não autorizado"):
        super().__init__(message, 401)

class ForbiddenError(SemapaException):
    """Acesso proibido"""
    def __init__(self, message="Acesso proibido"):
        super().__init__(message, 403)

def register_error_handlers(app):
    """Registra handlers de erro personalizados"""

    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({'error': 'Requisição inválida'}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({'error': 'Não autorizado'}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({'error': 'Acesso proibido'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'error': 'Recurso não encontrado'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.is_json:
            return jsonify({'error': 'Erro interno do servidor'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(SemapaException)
    def handle_semapa_exception(error):
        if request.is_json:
            return jsonify({'error': error.message}), error.status_code
        return render_template('errors/custom.html', error=error), error.status_code
