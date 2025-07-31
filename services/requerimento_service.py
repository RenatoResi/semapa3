# -*- coding: utf-8 -*-
"""
SEMAPA3 - Requerimento Service
Serviço de gerenciamento de requerimentos
"""

from models.requerimento_model import Requerimento
from models.requerente_model import Requerente
from models.arvore_model import Arvore
from models.user_model import User
from core.exceptions import ValidationError, NotFoundError

class RequerimentoService:
    """Serviço de gerenciamento de requerimentos"""

    @staticmethod
    def create(requerente_id, arvore_id, usuario_id, tipo, descricao, observacoes=None):
        """Cria novo requerimento"""
        if not all([requerente_id, arvore_id, usuario_id, tipo, descricao]):
            raise ValidationError("Todos os campos obrigatórios devem ser preenchidos")

        # Validar tipo
        if tipo not in ['poda', 'remocao', 'transplante']:
            raise ValidationError("Tipo deve ser: poda, remoção ou transplante")

        # Validar se entidades existem
        if not Requerente.query.get(requerente_id):
            raise ValidationError("Requerente não encontrado")

        if not Arvore.query.get(arvore_id):
            raise ValidationError("Árvore não encontrada")

        if not User.query.get(usuario_id):
            raise ValidationError("Usuário não encontrado")

        numero = Requerimento.generate_numero()
        requerimento = Requerimento(
            numero=numero,
            requerente_id=requerente_id,
            arvore_id=arvore_id,
            usuario_id=usuario_id,
            tipo=tipo,
            descricao=descricao,
            observacoes=observacoes
        )
        return requerimento.save()

    @staticmethod
    def update(requerimento_id, **kwargs):
        """Atualiza requerimento"""
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")

        if not requerimento.pode_editar:
            raise ValidationError("Requerimento não pode ser editado neste status")

        # Atualizar campos
        for key, value in kwargs.items():
            if hasattr(requerimento, key) and key not in ['id', 'numero', 'data_abertura']:
                setattr(requerimento, key, value)

        return requerimento.save()

    @staticmethod
    def aprovar(requerimento_id):
        """Aprova requerimento"""
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")

        requerimento.aprovar()
        return requerimento

    @staticmethod
    def negar(requerimento_id):
        """Nega requerimento"""
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")

        requerimento.negar()
        return requerimento

    @staticmethod
    def concluir(requerimento_id):
        """Conclui requerimento"""
        requerimento = Requerimento.query.get(requerimento_id)
        if not requerimento:
            raise NotFoundError("Requerimento não encontrado")

        requerimento.concluir()
        return requerimento

    @staticmethod
    def get_by_status(status):
        """Retorna requerimentos por status"""
        return Requerimento.get_by_status(status)

    @staticmethod
    def get_statistics():
        """Retorna estatísticas dos requerimentos"""
        return {
            'total': Requerimento.query.count(),
            'pendentes': Requerimento.query.filter_by(status='pendente').count(),
            'aprovados': Requerimento.query.filter_by(status='aprovado').count(),
            'negados': Requerimento.query.filter_by(status='negado').count(),
            'concluidos': Requerimento.query.filter_by(status='concluido').count()
        }
