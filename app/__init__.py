from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from datetime import datetime
from app.models.models import db, Usuario


csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @app.context_processor
    def injectar_ano_atual():
        return {"current_year": datetime.now().year}

    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def erro_interno(e):
        return render_template("500.html"), 500

    from app.routes import auth_bp, main_bp
    from app.routes.futebol import futebol_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(futebol_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
