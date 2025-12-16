from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app import models

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    with app.app_context():
        db.create_all()

        # ------------------------------------
        # AUTO-CREATE DEFAULT USERS FOR DEMO
        # ------------------------------------
        from app.models import User

        if User.query.count() == 0:
            student = User(
                username="testuser",
                role="student"
            )
            instructor = User(
                username="instructor",
                role="instructor"
            )

            db.session.add_all([student, instructor])
            db.session.commit()

            print("Created default users:")
            print(" - testuser (student)")
            print(" - instructor (instructor)")

    return app
