from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
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

    from app.routes import auth_bp, main_bp
    from app.routes.futebol import futebol_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(futebol_bp)


    return app

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
