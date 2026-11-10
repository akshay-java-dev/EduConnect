
import os

from flask import Flask
from config import Config

from .extensions import db, login_manager, bcrypt, csrf


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load application configuration
    app.config.from_object(Config)

    # Create instance and upload folders
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    # Import models
    from . import models
    from .models import User

    # Import blueprints
    from .auth import auth
    from .main import main
    from .admin import admin
    from .student import student

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(student, url_prefix="/student")

    # Load logged-in user
    @login_manager.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))

    # Database initialization command
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created successfully.")

    # Create admin command
    @app.cli.command("create-admin")
    def create_admin():
        import getpass

        email = input("Admin email: ").strip().lower()
        name = input("Admin name: ").strip()
        password = getpass.getpass("Admin password: ")

        if User.query.filter_by(email=email).first():
            print("Email already exists.")
            return

        user = User(
            name=name,
            email=email,
            role="admin"
        )

        user.set_password(password, bcrypt)

        db.session.add(user)
        db.session.commit()

        print("Admin created successfully.")

    # Automatically create missing tables on application startup
    with app.app_context():
        db.create_all()
        print("EduConnect database initialized successfully.")

    return app
