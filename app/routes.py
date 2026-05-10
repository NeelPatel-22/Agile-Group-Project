import os
import uuid

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.utils import secure_filename

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
from .models import Recipe, User
main = Blueprint("main", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def is_allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return ""

    if not is_allowed_image(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(upload_path)
    return f"uploads/{unique_name}"
 
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
    recipe = get_recipe_with_author(recipe_id)
    if not recipe:
        abort(404)

    more_recipes = [
        attach_author(item)
        for item in recipes_data
        if item["author_id"] == recipe["author"]["id"] and item["id"] != recipe_id
    ]
    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        more_recipes=more_recipes,
    )


@main.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        abort(404)

    error = None
    success = None
    form_recipe = recipe_to_form(recipe)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        cook_time_raw = request.form.get("cook_time", "").strip()
        servings_raw = request.form.get("servings", "").strip()
        description = request.form.get("description", "").strip()
        ingredients_raw = request.form.get("ingredients", "").strip()
        steps_raw = request.form.get("steps", "").strip()

        form_recipe = {
            "id": recipe["id"],
            "title": title,
            "category": category,
            "cook_time": cook_time_raw,
            "servings": servings_raw,
            "description": description,
            "why_people_love_it": request.form.get("why_people_love_it", "").strip(),
            "flavor_notes": request.form.get("flavor_notes", "").strip(),
            "skill_level": request.form.get("skill_level", "").strip(),
            "best_for": request.form.get("best_for", "").strip(),
            "pair_with": request.form.get("pair_with", "").strip(),
            "spice_level": request.form.get("spice_level", "").strip(),
            "dietary_cautions": request.form.get("dietary_cautions", "").strip(),
            "ingredients": ingredients_raw,
            "steps": steps_raw,
            "image_url": request.form.get("image_url", "").strip() or recipe.get("image_url", ""),
        }

        if not title or not description or not ingredients_raw or not steps_raw:
            error = "Title, description, ingredients, and steps are required."
        else:
            ingredient_lines = [line.strip() for line in ingredients_raw.splitlines() if line.strip()]
            step_lines = [line.strip() for line in steps_raw.splitlines() if line.strip()]

            recipe["title"] = title
            recipe["category"] = category or recipe.get("category", "")
            recipe["cook_time"] = int(cook_time_raw) if cook_time_raw.isdigit() else cook_time_raw
            recipe["servings"] = int(servings_raw) if servings_raw.isdigit() else servings_raw
            recipe["description"] = description
            recipe["overview"] = description
            recipe["why_people_love_it"] = form_recipe["why_people_love_it"]
            recipe["flavor_notes"] = form_recipe["flavor_notes"]
            recipe["skill_level"] = form_recipe["skill_level"]
            recipe["difficulty"] = form_recipe["skill_level"] or recipe.get("difficulty", "")
            recipe["best_for"] = form_recipe["best_for"]
            recipe["pair_with"] = form_recipe["pair_with"]
            recipe["spice_level"] = form_recipe["spice_level"]
            recipe["dietary_cautions"] = form_recipe["dietary_cautions"]
            recipe["ingredients"] = ingredient_lines
            recipe["steps"] = [
                {"title": f"Step {index}", "description": step}
                for index, step in enumerate(step_lines, start=1)
            ]
            recipe["image_url"] = form_recipe["image_url"]
            form_recipe = recipe_to_form(recipe)
            success = "Recipe changes saved."

    return render_template(
        "edit_recipe.html",
        recipe=form_recipe,
        error=error,
        success=success,
    )


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
 
 
@main.route("/add-recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        cook_time = request.form.get("cook_time", "").strip()
        servings = request.form.get("servings", "").strip()
        description = request.form.get("description", "").strip()
        why_people_love_it = request.form.get("why_people_love_it", "").strip()
        flavor_notes = request.form.get("flavor_notes", "").strip()
        skill_level = request.form.get("skill_level", "").strip()
        best_for = request.form.get("best_for", "").strip()
        pair_with = request.form.get("pair_with", "").strip()
        spice_level = request.form.get("spice_level", "").strip()
        dietary_cautions = request.form.get("dietary_cautions", "").strip()
        ingredients = request.form.get("ingredients", "").strip()
        steps = request.form.get("steps", "").strip()
        image_url = request.form.get("image_url", "").strip()
        image_file = request.files.get("image_file")

        if not title or not description or not ingredients or not steps:
            error = "Please complete all required recipe fields."
        else:
            if image_file and image_file.filename:
                uploaded_image = save_uploaded_image(image_file)
                if uploaded_image is None:
                    error = "Upload a PNG, JPG, JPEG, GIF, or WEBP image."
                else:
                    image_url = uploaded_image

            if error is None:
                recipe = Recipe(
                    title=title,
                    category=category,
                    cook_time=cook_time,
                    servings=servings,
                    description=description,
                    why_people_love_it=why_people_love_it,
                    flavor_notes=flavor_notes,
                    skill_level=skill_level,
                    best_for=best_for,
                    pair_with=pair_with,
                    spice_level=spice_level,
                    dietary_cautions=dietary_cautions,
                    ingredients=ingredients,
                    steps=steps,
                    image_url=image_url,
                    user_id=current_user.id,
                )
                db.session.add(recipe)
                db.session.commit()
                return redirect(url_for("main.profile", user_id=current_user.id))

    return render_template("add_recipe.html", error=error)
 
 
@main.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    member_since = user.created_at.strftime("%B %Y")
    own_recipes = Recipe.query.filter_by(user_id=user.id).order_by(Recipe.created_at.desc()).all()

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        own_recipes=own_recipes,
    )


@main.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    if user_id != current_user.id:
        abort(403)

    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        bio = request.form.get("bio", "").strip()
        profile_image_file = request.files.get("profile_image")
        existing_user = User.query.filter(
            ((User.email == email) | (User.username == username)) & (User.id != current_user.id)
        ).first()

        if not username or not email:
            error = "Username and email are required."
        elif not is_valid_email(email):
            error = "Please enter a real email address."
        elif existing_user:
            error = "That username or email is already in use."
        else:
            profile_image = save_uploaded_image(profile_image_file)
            if profile_image is None:
                error = "Upload a PNG, JPG, JPEG, GIF, or WEBP image."
            else:
                current_user.username = username
                current_user.email = email
                current_user.bio = bio
                if profile_image:
                    current_user.profile_image = profile_image
                db.session.commit()
                return redirect(url_for("main.profile", user_id=current_user.id))

    return render_template(
        "edit_profile.html",
        error=error,
        success=success,
    )
