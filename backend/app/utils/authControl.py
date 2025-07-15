from functools import wraps
from flask_jwt_extended import jwt_required, current_user
from flask import request, abort

def mod_required(fn):
    """Decorater for Mod Authentication"""
    @wraps(fn)
    # @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

def doc_required(fn):
    """Decorater for Mod Authentication"""
    @wraps(fn)
    # @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

def sen_required(fn):
    """Decorater for Mod Authentication"""
    @wraps(fn)
    # @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper