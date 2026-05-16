import hmac
import os
import secrets

from flask import Flask, abort, request, session
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


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf_token():
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return

    expected_token = session.get("_csrf_token")
    submitted_token = request.form.get("_csrf_token") or request.headers.get("X-CSRFToken")

    if not expected_token or not submitted_token or not hmac.compare_digest(expected_token, submitted_token):
        abort(400, description="Invalid or missing CSRF token.")


def run_sqlite_migrations():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    statements = []
    if "comment" in tables:
        comment_columns = {column["name"] for column in inspector.get_columns("comment")}

        if "is_hidden" not in comment_columns:
            statements.append("ALTER TABLE comment ADD COLUMN is_hidden BOOLEAN DEFAULT 0 NOT NULL")

        if "parent_id" not in comment_columns:
            statements.append("ALTER TABLE comment ADD COLUMN parent_id INTEGER")

    if "recipe" in tables:
        recipe_columns = {column["name"] for column in inspector.get_columns("recipe")}

        if "is_archived" not in recipe_columns:
            statements.append("ALTER TABLE recipe ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL")

        if "archived_at" not in recipe_columns:
            statements.append("ALTER TABLE recipe ADD COLUMN archived_at DATETIME")

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
    app.config["CSRF_PROTECTION_ENABLED"] = env_bool("CSRF_PROTECTION_ENABLED", True)
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

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": csrf_token}

    @app.before_request
    def protect_post_requests():
        if app.config.get("CSRF_PROTECTION_ENABLED", True):
            validate_csrf_token()

    with app.app_context():
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        configure_sqlite_connection()
        db.create_all()
        run_sqlite_migrations()

    return app
