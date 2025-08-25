# -*- coding: utf-8 -*-
"""
SEMAPA3 - Auth Controller
Autenticação e Cadastro de Usuários
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
from core.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Preencha todos os campos!', 'warning')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Usuário ou senha inválidos.', 'danger')
            return render_template('auth/login.html')
        if not user.ativo:
            flash('Usuário está inativo.', 'danger')
            return render_template('auth/login.html')

        login_user(user)
        flash('Login efetuado com sucesso!', 'success')
        next_url = request.args.get('next') or url_for('dashboard.index')
        return redirect(next_url)
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout efetuado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')

        if not nome or not email or not password:
            flash('Preencha todos os campos!', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('E-mail já está cadastrado.', 'danger')
            return render_template('auth/register.html')

        novo = User(email=email, password=password, nome=nome, nivel=4, ativo=True)
        db.session.add(novo)
        db.session.commit()
        flash('Cadastro realizado! Você já pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
