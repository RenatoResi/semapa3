# -*- coding: utf-8 -*-
"""
SEMAPA3 - Auth Controller
Controller de autenticação e autorização
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService
from core.exceptions import ValidationError, UnauthorizedError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            user = AuthService.login(email, password)
            login_user(user, remember=True)

            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page or url_for('dashboard.index'))

        except (ValidationError, UnauthorizedError) as e:
            flash(str(e), 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novo usuário"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')

            AuthService.register(nome, email, senha)
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('auth.login'))

        except ValidationError as e:
            flash(str(e), 'error')

    return render_template('auth/register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Alterar senha"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        AuthService.change_password(current_user, current_password, new_password)
        flash('Senha alterada com sucesso!', 'success')

    except ValidationError as e:
        flash(str(e), 'error')

    return redirect(url_for('auth.profile'))
