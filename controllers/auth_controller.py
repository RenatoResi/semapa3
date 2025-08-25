# -*- coding: utf-8 -*-
"""
SEMAPA3 - Auth Controller CORRECTED
Autenticação e Cadastro de Usuários - CORRIGIDO
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from services.auth_service import AuthService
from core.database import db
from core.exceptions import ValidationError, UnauthorizedError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """CORRIGIDO: Agora usa AuthService e trata erros adequadamente"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Preencha todos os campos!', 'warning')
            return render_template('auth/login.html')

        try:
            # CORRIGIDO: Usar AuthService que trata validação e autenticação
            user = AuthService.login(email, password)
            login_user(user)
            flash('Login efetuado com sucesso!', 'success')
            next_url = request.args.get('next') or url_for('dashboard.index')
            return redirect(next_url)
            
        except ValidationError as e:
            flash(f'Erro de validação: {e.message}', 'danger')
        except UnauthorizedError as e:
            flash(f'Erro de autenticação: {e.message}', 'danger')
        except Exception as e:
            flash(f'Erro interno: {str(e)}', 'danger')
        
        return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout efetuado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """CORRIGIDO: Agora usa AuthService e hasheia senha corretamente"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not nome or not email or not password:
            flash('Preencha todos os campos!', 'warning')
            return render_template('auth/register.html')

        try:
            # CORRIGIDO: Usar AuthService que valida e cria usuário com senha hash
            user = AuthService.register(nome=nome, email=email, senha=password, nivel=4)
            flash('Cadastro realizado com sucesso! Você já pode fazer login.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValidationError as e:
            flash(f'Erro: {e.message}', 'danger')
        except Exception as e:
            flash(f'Erro interno: {str(e)}', 'danger')
        
        return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """NOVO: Rota para alterar senha usando AuthService"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not all([current_password, new_password, confirm_password]):
        flash('Preencha todos os campos!', 'warning')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('Nova senha e confirmação não coincidem!', 'danger')
        return redirect(url_for('auth.profile'))

    try:
        AuthService.change_password(current_user, current_password, new_password)
        flash('Senha alterada com sucesso!', 'success')
    except ValidationError as e:
        flash(f'Erro: {e.message}', 'danger')
    except Exception as e:
        flash(f'Erro interno: {str(e)}', 'danger')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Página de perfil do usuário"""
    return render_template('auth/profile.html')