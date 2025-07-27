# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerente Service
Serviço de gerenciamento de requerentes
"""

from models.requerente_model import Requerente
from core.exceptions import ValidationError, NotFoundError
import re

class RequerenteService:
    """Serviço de gerenciamento de requerentes"""

    @staticmethod
    def create(nome, cpf_cnpj, tipo, telefone=None, email=None, endereco=None):
        """Cria novo requerente"""
        if not all([nome, cpf_cnpj, tipo]):
            raise ValidationError("Nome, CPF/CNPJ e tipo são obrigatórios")

        # Validar tipo
        if tipo not in ['pf', 'pj']:
            raise ValidationError("Tipo deve ser 'pf' ou 'pj'")

        # Validar CPF/CNPJ único
        if Requerente.find_by_cpf_cnpj(cpf_cnpj):
            raise ValidationError("CPF/CNPJ já cadastrado")

        # Validar email se fornecido
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError("Formato de email inválido")

        requerente = Requerente(
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            tipo=tipo,
            telefone=telefone,
            email=email,
            endereco=endereco
        )
        return requerente.save()

    @staticmethod
    def update(requerente_id, **kwargs):
        """Atualiza dados do requerente"""
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")

        # Validar email se fornecido
        if 'email' in kwargs and kwargs['email']:
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', kwargs['email']):
                raise ValidationError("Formato de email inválido")

        # Atualizar campos
        for key, value in kwargs.items():
            if hasattr(requerente, key):
                setattr(requerente, key, value)

        return requerente.save()

    @staticmethod
    def delete(requerente_id):
        """Remove requerente"""
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")

        # Verificar se tem requerimentos
        if requerente.total_requerimentos > 0:
            raise ValidationError("Não é possível remover requerente com requerimentos")

        requerente.delete()
        return True

    @staticmethod
    def get_by_id(requerente_id):
        """Busca requerente por ID"""
        requerente = Requerente.query.get(requerente_id)
        if not requerente:
            raise NotFoundError("Requerente não encontrado")
        return requerente

    @staticmethod
    def search(query, page=1, per_page=10):
        """Busca requerentes com paginação"""
        if query:
            requerentes = Requerente.search(query)
        else:
            requerentes = Requerente.query.order_by(Requerente.nome).all()

        # Implementar paginação manual
        start = (page - 1) * per_page
        end = start + per_page
        return requerentes[start:end], len(requerentes)

    @staticmethod
    def get_all(page=1, per_page=10):
        """Lista todos os requerentes com paginação"""
        pagination = Requerente.query.order_by(Requerente.nome).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination.items, pagination.total
