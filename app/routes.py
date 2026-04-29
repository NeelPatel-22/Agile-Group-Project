from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired

from . import db
from .helpers.email_helpers import (
    get_email_from_confirmation_token,
    is_valid_email,
    send_confirmation_email,
)
from .helpers.recipe_helpers import (
    get_more_recipes_by_author,
    get_recipe_by_id,
    get_recipes_by_user,
    get_user_by_id,
)
from .models import User
main = Blueprint("main", __name__)
 
@main.route("/")
def cover():
    if current_user.is_authenticated:
        return redirect(url_for("main.recipes"))

    return render_template("cover.html")
 
 
@main.route("/recipes")
def recipes():
    return render_template("recipes.html", recipes=[])
 
 
@main.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        abort(404)

    more_recipes = get_more_recipes_by_author(recipe["author"]["id"], recipe["id"])
    return render_template("recipe_detail.html", recipe=recipe, more_recipes=more_recipes)
 
 
@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.recipes"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.email_confirmed:
                send_confirmation_email(user)
                return render_template("check_email.html", email=user.email)

            login_user(user)
            return redirect(url_for("main.recipes"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)
 
 
@main.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.recipes"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        bio = request.form.get("bio", "").strip()

        if not username or not email or not password:
            error = "Please fill in all fields."
        elif not is_valid_email(email):
            error = "Please enter a real email address."
        elif User.query.filter((User.email == email) | (User.username == username)).first():
            error = "A user with that email or username already exists."
        else:
            user = User(username=username, email=email, bio=bio)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            send_confirmation_email(user)
            return render_template("check_email.html", email=user.email)

    return render_template("signup.html", error=error)


@main.route("/confirm-email/<token>")
def confirm_email(token):
    try:
        email = get_email_from_confirmation_token(token)
    except SignatureExpired:
        return render_template(
            "login.html",
            error="That confirmation link has expired. Log in to receive a new one.",
        )
    except BadSignature:
        return render_template("login.html", error="That confirmation link is invalid.")

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template("login.html", error="No account was found for that confirmation link.")

    user.email_confirmed = True
    db.session.commit()
    logout_user()
    return redirect(url_for("main.login"))

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.cover"))
 
 
@main.route("/add-recipe")
def add_recipe():
    return render_template("add_recipe.html")
 
 
@main.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user_by_id(user_id)

    if not user:
        abort(404)

    user_recipes = get_recipes_by_user(user_id)
    user_with_count = user.copy()
    user_with_count["recipe_count"] = len(user_recipes)

    return render_template(
        "profile.html",
        user=user_with_count,
        user_recipes=user_recipes,
    )


@main.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
def edit_profile(user_id):
    user = get_user_by_id(user_id)

    if not user:
        abort(404)

    error = None
    success = None
    form_user = user.copy()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        bio = request.form.get("bio", "").strip()

        if not username or not email:
            error = "Username and email are required."
            form_user["name"] = username
            form_user["email"] = email
            form_user["bio"] = bio
        else:
            user["name"] = username
            user["email"] = email
            user["bio"] = bio
            form_user = user.copy()
            success = "Profile changes saved."

    return render_template(
        "edit_profile.html",
        user=form_user,
        error=error,
        success=success,
    )
