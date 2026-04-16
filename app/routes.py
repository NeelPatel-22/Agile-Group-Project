from app.routes_auth import auth_bp
from app.routes_core import core_bp
from app.routes_profile import profile_bp
from app.routes_recipes import recipes_bp


def register_routes(app):
    app.register_blueprint(core_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
