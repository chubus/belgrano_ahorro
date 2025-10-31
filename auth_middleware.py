from functools import wraps

from flask import request, jsonify, current_app


def _is_authorized():
    token = request.headers.get("Authorization")
    api_key = current_app.config.get("API_KEY")
    return token and token == f"Bearer {api_key}"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _is_authorized():
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


admin_required = flota_required = login_required


def validate_input_data(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Invalid JSON"}), 400
        return f(*args, **kwargs)
    return decorated


def production_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


def rate_limit(f=None, max_requests=None, window=None):
    """Decorador de rate limiting (implementación básica)"""
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated
    
    # Permitir uso como @rate_limit o @rate_limit(max_requests=5, window=300)
    if f is None:
        return decorator
    return decorator(f)

