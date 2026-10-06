from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_caching import Cache
from datetime import datetime
from app.models import db, Usuario


csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 600})

def create_app():
    """Inicializa e configura a aplicação Flask, extensões e blueprints."""
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)

    with app.app_context():
        db.create_all()

    @app.context_processor
    def injectar_ano_atual():
        """Injeta o ano atual nos templates para exibição no rodapé."""
        return {"current_year": datetime.now().year}

    @app.errorhandler(404)
    def nao_encontrado(e):
        """Renderiza a página personalizada para erro 404."""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def erro_interno(e):
        """Renderiza a página personalizada para erro 500."""
        return render_template("500.html"), 500

    from app.routes import auth_bp, main_bp, futebol_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(futebol_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário autenticado a partir do ID armazenado na sessão."""
    return Usuario.query.get(int(user_id))
