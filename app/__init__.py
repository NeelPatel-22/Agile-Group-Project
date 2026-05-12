import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from dotenv import load_dotenv
from sqlalchemy import inspect, text

load_dotenv()

# database-setup
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def run_sqlite_migrations():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    statements = []
    if "comment" in tables:
        comment_columns = {column["name"] for column in inspector.get_columns("comment")}

        if "is_hidden" not in comment_columns:
            statements.append("ALTER TABLE comment ADD COLUMN is_hidden BOOLEAN DEFAULT 0 NOT NULL")

    if "user" in tables:
        user_columns = {column["name"] for column in inspector.get_columns("user")}

        if "bio" not in user_columns:
            statements.append("ALTER TABLE user ADD COLUMN bio VARCHAR(255) DEFAULT ''")

        if "profile_image" not in user_columns:
            statements.append("ALTER TABLE user ADD COLUMN profile_image VARCHAR(255) DEFAULT ''")

        if "email_confirmed" not in user_columns:
            statements.append("ALTER TABLE user ADD COLUMN email_confirmed BOOLEAN DEFAULT 0 NOT NULL")

    for statement in statements:
        db.session.execute(text(statement))

    if statements:
        db.session.commit()


def configure_sqlite_connection():
    if db.engine.url.get_backend_name() != "sqlite":
        return

    db.session.execute(text("PRAGMA journal_mode=MEMORY"))
    db.session.execute(text("PRAGMA synchronous=NORMAL"))
    db.session.execute(text("PRAGMA foreign_keys=ON"))
    db.session.commit()


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "recipes123")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///recipes.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = env_bool("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.static_folder,
        os.environ.get("UPLOAD_FOLDER", "uploads"),
    )
    app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = env_bool("MAIL_USE_TLS", True)
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@recipehub.local")
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    login_manager.login_view = "main.login"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        configure_sqlite_connection()
        db.create_all()
        run_sqlite_migrations()

    return app
