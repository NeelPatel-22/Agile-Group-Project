from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    bio = db.Column(db.String(255), default="")
    profile_image = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    recipes = db.relationship("Recipe", backref="author", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="author", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), default="")
    cook_time = db.Column(db.String(80), default="")
    servings = db.Column(db.String(80), default="")
    description = db.Column(db.Text, nullable=False)
    why_people_love_it = db.Column(db.Text, default="")
    flavor_notes = db.Column(db.String(255), default="")
    skill_level = db.Column(db.String(120), default="")
    best_for = db.Column(db.String(255), default="")
    pair_with = db.Column(db.String(255), default="")
    spice_level = db.Column(db.String(120), default="")
    dietary_cautions = db.Column(db.Text, default="")
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    comments = db.relationship(
        "Comment",
        backref="recipe",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(Comment.created_at)",
    )

    def ingredient_list(self):
        return [item.strip() for item in self.ingredients.splitlines() if item.strip()]

    def step_list(self):
        return [item.strip() for item in self.steps.splitlines() if item.strip()]

    def short_author_role(self):
        return self.author.bio if self.author and self.author.bio else "Recipe creator"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
