import os
import sqlite3

from flask import Flask


def initialize_database(app):
    database_path = app.config["DATABASE_PATH"]

    with sqlite3.connect(database_path):
        pass

    print(f"Database connected ~ recipes.db ")


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "dev-secret-key-change-this"
    app.config["DATABASE_PATH"] = os.path.join(app.instance_path, "recipes.db")

    os.makedirs(app.instance_path, exist_ok=True)
    initialize_database(app)

    from .routes import main

    app.register_blueprint(main)
    return app
