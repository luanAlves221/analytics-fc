from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from urllib.parse import urlsplit
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Usuario
from app.forms.auth_forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Exibe e processa o formulário de cadastro de novos usuários."""
    form = RegisterForm()

    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data

        existing_user = Usuario.query.filter_by(email=email).first()

        if existing_user:
            flash("Email já cadastrado. Tente novamente.")
            return render_template("register.html", form=form)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Conta criada com sucesso. Faça login.")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Exibe e processa o formulário de login do usuário."""
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data

        user = Usuario.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.senha, senha):
            flash("Email ou senha incorretos. Tente novamente.")
            return render_template("login.html", form=form)

        login_user(user)
        next_page = request.args.get("next")
        if next_page:
            parts = urlsplit(next_page)
            if not parts.scheme and not parts.netloc and next_page.startswith("/"):
                return redirect(next_page)
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """Encerra a sessão do usuário autenticado e redireciona para o login."""
    logout_user()
    return redirect(url_for("auth.login"))
