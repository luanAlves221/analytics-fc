from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Renderiza a página inicial de apresentação do Analytics FC."""
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Renderiza o painel principal de estatísticas e análises para o usuário logado."""
    return render_template("dashboard.html", usuario=current_user)
