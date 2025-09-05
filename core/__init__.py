# -*- coding: utf-8 -*-
"""
SEMAPA3 - Core Package
Núcleo da aplicação com funcionalidades essenciais
"""

from .database import db, BaseModel
from .security import login_manager, require_role, SecurityMixin
from .exceptions import (
    SemapaException, 
    ValidationError, 
    NotFoundError, 
    UnauthorizedError, 
    ForbiddenError,
    register_error_handlers
)

__all__ = [
    'db',
    'BaseModel',
    'login_manager',  
    'csrf',
    'require_role',
    'SecurityMixin',
    'SemapaException',
    'ValidationError',
    'NotFoundError',
    'UnauthorizedError', 
    'ForbiddenError',
    'register_error_handlers'
]
