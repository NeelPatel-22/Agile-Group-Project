import os
import uuid

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from . import db, socketio
from .helpers.email_helpers import (
    get_payload_from_confirmation_token,
    get_payload_from_email_change_token,
    get_payload_from_password_reset_token,
    is_valid_email,
    send_email_change_confirmation,
    send_password_reset_email,
    send_signup_confirmation_email,
)
from .helpers.recipe_helpers import (
    get_more_recipes_by_author,
    get_recipe_by_id,
    get_recipes_by_user,
    get_user_by_id,
)
from .models import Comment, Like, PendingSignup, Recipe, SavedRecipe, User
main = Blueprint("main", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MIN_PASSWORD_LENGTH = 8


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


def distinct_recipe_values(column):
    rows = db.session.query(column).filter(column.isnot(None), column != "").distinct().order_by(column.asc()).all()
    return [value for (value,) in rows if value]


def visible_comment_count(recipe):
    return len([comment for comment in recipe.comments if not comment.is_hidden])


def recipe_payload(recipe, user=None):
    user = user or current_user
    liked = False
    saved = False

    if getattr(user, "is_authenticated", False):
        liked = any(like.user_id == user.id for like in recipe.likes)
        saved = any(save.user_id == user.id for save in recipe.saves)

    return {
        "id": recipe.id,
        "likes_count": len(recipe.likes),
        "saves_count": len(recipe.saves),
        "comments_count": visible_comment_count(recipe),
        "liked": liked,
        "saved": saved,
    }


def broadcast_recipe_update(recipe):
    socketio.emit(
        "recipe_updated",
        {
            "id": recipe.id,
            "likes_count": len(recipe.likes),
            "saves_count": len(recipe.saves),
            "comments_count": visible_comment_count(recipe),
        },
    )
 
@main.route("/")
def cover():
    if current_user.is_authenticated:
        return redirect(url_for("main.recipes"))

    return render_template("cover.html")
 
 
@main.route("/recipes")
@login_required
def recipes():
    filters = {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", "").strip(),
        "skill_level": request.args.get("skill_level", "").strip(),
        "spice_level": request.args.get("spice_level", "").strip(),
        "best_for": request.args.get("best_for", "").strip(),
        "cook_time": request.args.get("cook_time", "").strip(),
        "servings": request.args.get("servings", "").strip(),
    }

    recipe_query = Recipe.query.order_by(Recipe.created_at.desc())

    if filters["q"]:
        like_term = f"%{filters['q']}%"
        recipe_query = recipe_query.filter(
            (Recipe.title.ilike(like_term))
            | (Recipe.description.ilike(like_term))
            | (Recipe.ingredients.ilike(like_term))
            | (Recipe.category.ilike(like_term))
            | (Recipe.flavor_notes.ilike(like_term))
            | (Recipe.best_for.ilike(like_term))
            | (Recipe.pair_with.ilike(like_term))
        )

    if filters["category"]:
        recipe_query = recipe_query.filter(Recipe.category == filters["category"])

    if filters["skill_level"]:
        recipe_query = recipe_query.filter(Recipe.skill_level == filters["skill_level"])

    if filters["spice_level"]:
        recipe_query = recipe_query.filter(Recipe.spice_level == filters["spice_level"])

    if filters["best_for"]:
        recipe_query = recipe_query.filter(Recipe.best_for.ilike(f"%{filters['best_for']}%"))

    if filters["cook_time"]:
        recipe_query = recipe_query.filter(Recipe.cook_time.ilike(f"%{filters['cook_time']}%"))

    if filters["servings"]:
        recipe_query = recipe_query.filter(Recipe.servings.ilike(f"%{filters['servings']}%"))

    all_recipes = recipe_query.all()
    filter_options = {
        "categories": distinct_recipe_values(Recipe.category),
        "skill_levels": distinct_recipe_values(Recipe.skill_level),
        "spice_levels": distinct_recipe_values(Recipe.spice_level),
    }
    active_filter_count = sum(1 for value in filters.values() if value)

    return render_template(
        "recipes.html",
        recipes=all_recipes,
        filters=filters,
        filter_options=filter_options,
        active_filter_count=active_filter_count,
    )
 
 
@main.route("/recipes/<int:recipe_id>")
@login_required
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    more_recipes = (
        Recipe.query.filter(Recipe.user_id == recipe.user_id, Recipe.id != recipe.id)
        .order_by(Recipe.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        more_recipes=more_recipes,
    )


@main.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    error = None

    if recipe.user_id != current_user.id:
        abort(403)

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
        image_url = request.form.get("image_url", "").strip() or recipe.image_url
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
                recipe.title = title
                recipe.category = category
                recipe.cook_time = cook_time
                recipe.servings = servings
                recipe.description = description
                recipe.why_people_love_it = why_people_love_it
                recipe.flavor_notes = flavor_notes
                recipe.skill_level = skill_level
                recipe.best_for = best_for
                recipe.pair_with = pair_with
                recipe.spice_level = spice_level
                recipe.dietary_cautions = dietary_cautions
                recipe.ingredients = ingredients
                recipe.steps = steps
                recipe.image_url = image_url
                db.session.commit()
                return redirect(url_for("main.recipe_detail", recipe_id=recipe.id))

    return render_template(
        "edit_recipe.html",
        recipe=recipe,
        error=error,
    )


@main.route("/recipes/<int:recipe_id>/like", methods=["POST"])
@login_required
def toggle_like(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    existing_like = Like.query.filter_by(recipe_id=recipe.id, user_id=current_user.id).first()

    if existing_like:
        db.session.delete(existing_like)
        action = "removed"
    else:
        db.session.add(Like(recipe_id=recipe.id, user_id=current_user.id))
        action = "added"

    db.session.commit()
    payload = recipe_payload(recipe)
    broadcast_recipe_update(recipe)
    return jsonify({"success": True, "action": action, **payload})


@main.route("/recipes/<int:recipe_id>/save", methods=["POST"])
@login_required
def toggle_save(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    existing_save = SavedRecipe.query.filter_by(recipe_id=recipe.id, user_id=current_user.id).first()

    if existing_save:
        db.session.delete(existing_save)
        action = "removed"
    else:
        db.session.add(SavedRecipe(recipe_id=recipe.id, user_id=current_user.id))
        action = "added"

    db.session.commit()
    payload = recipe_payload(recipe)
    broadcast_recipe_update(recipe)
    return jsonify({"success": True, "action": action, **payload})


@main.route("/recipes/<int:recipe_id>/comment", methods=["POST"])
@login_required
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    content = request.form.get("content", "").strip()

    if not content:
        return jsonify({"success": False, "message": "Comment cannot be empty."}), 400

    comment = Comment(content=content, recipe_id=recipe.id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()

    payload = {
        "recipe_id": recipe.id,
        "comment_id": comment.id,
        "comment_html": render_template("partials/comment_item.html", comment=comment, recipe=recipe),
        "comments_count": visible_comment_count(recipe),
    }
    socketio.emit("comment_added", payload)
    broadcast_recipe_update(recipe)
    return jsonify({"success": True, **payload})


@main.route("/comments/<int:comment_id>/hide", methods=["POST"])
@login_required
def hide_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.recipe.user_id != current_user.id:
        return jsonify({"success": False, "message": "Only the recipe owner can hide comments."}), 403

    comment.is_hidden = True
    db.session.commit()
    payload = {
        "recipe_id": comment.recipe_id,
        "comment_id": comment.id,
        "comments_count": visible_comment_count(comment.recipe),
    }
    socketio.emit("comment_hidden", payload)
    broadcast_recipe_update(comment.recipe)
    return jsonify({"success": True, **payload})
 
 
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
                error = "Please confirm your email before logging in."
                return render_template("login.html", error=error)

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
        profile_image_file = request.files.get("profile_image")

        existing_pending = PendingSignup.query.filter(
            (PendingSignup.email == email) | (PendingSignup.username == username)
        ).first()

        if not username or not email or not password:
            error = "Please fill in all fields."
        elif not is_valid_email(email):
            error = "Please enter a real email address."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        elif User.query.filter((User.email == email) | (User.username == username)).first():
            error = "A user with that email or username already exists."
        elif existing_pending:
            error = "A confirmation email has already been sent for that email or username."
        else:
            profile_image = save_uploaded_image(profile_image_file)
            if profile_image is None:
                error = "Upload a PNG, JPG, JPEG, GIF, or WEBP image."
            else:
                pending_signup = PendingSignup(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    bio=bio,
                    profile_image=profile_image or "",
                )
                db.session.add(pending_signup)
                db.session.commit()

                confirmation_url = send_signup_confirmation_email(pending_signup)
                return render_template(
                    "check_email.html",
                    email=email,
                    development_confirmation_url=confirmation_url if not current_app.config.get("MAIL_SERVER") else None,
                )

    return render_template("signup.html", error=error)


@main.route("/confirm-email/<token>")
def confirm_email(token):
    try:
        payload = get_payload_from_confirmation_token(token)
    except SignatureExpired:
        return render_template(
            "signup.html",
            error="That confirmation link has expired. Please sign up again.",
        )
    except BadSignature:
        return render_template("signup.html", error="That confirmation link is invalid.")

    if not isinstance(payload, dict) or "pending_signup_id" not in payload:
        return render_template("signup.html", error="That confirmation link is invalid.")

    pending_signup = db.session.get(PendingSignup, payload["pending_signup_id"])
    if not pending_signup:
        return render_template("signup.html", error="That confirmation link is invalid or has already been used.")

    email = pending_signup.email.strip().lower()
    username = pending_signup.username.strip()

    if User.query.filter((User.email == email) | (User.username == username)).first():
        db.session.delete(pending_signup)
        db.session.commit()
        return render_template("login.html", error="That account already exists. Please log in.")

    user = User(
        username=username,
        email=email,
        password_hash=pending_signup.password_hash,
        email_confirmed=True,
        bio=pending_signup.bio,
        profile_image=pending_signup.profile_image,
    )

    db.session.add(user)
    db.session.delete(pending_signup)
    db.session.commit()
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.recipes"))

    error = None
    sent = False

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            error = "Please enter your email address."
        elif not is_valid_email(email):
            error = "Please enter a real email address."
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                send_password_reset_email(user)
            sent = True

    return render_template("forgot_password.html", error=error, sent=sent)


@main.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        logout_user()

    error = None

    try:
        payload = get_payload_from_password_reset_token(token)
    except SignatureExpired:
        return render_template("forgot_password.html", error="That reset link has expired.", sent=False)
    except BadSignature:
        return render_template("forgot_password.html", error="That reset link is invalid.", sent=False)

    user = db.session.get(User, payload.get("user_id")) if isinstance(payload, dict) else None
    if not user:
        return render_template("forgot_password.html", error="That reset link is invalid.", sent=False)

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not password:
            error = "Please enter a new password."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            user.set_password(password)
            db.session.commit()
            return render_template("login.html", error=None, success="Your password has been reset. Please log in.")

    return render_template("reset_password.html", error=error)


@main.route("/confirm-email-change/<token>")
def confirm_email_change(token):
    try:
        payload = get_payload_from_email_change_token(token)
    except SignatureExpired:
        return render_template("login.html", error="That email change link has expired.")
    except BadSignature:
        return render_template("login.html", error="That email change link is invalid.")

    user = db.session.get(User, payload.get("user_id")) if isinstance(payload, dict) else None
    new_email = payload.get("email", "").strip().lower() if isinstance(payload, dict) else ""

    if not user or not new_email:
        return render_template("login.html", error="That email change link is invalid.")

    existing_user = User.query.filter((User.email == new_email) & (User.id != user.id)).first()
    if existing_user:
        return render_template("login.html", error="That email address is already in use.")

    user.email = new_email
    user.email_confirmed = True
    db.session.commit()
    logout_user()
    return render_template("login.html", error=None, success="Your email has been updated. Please log in again.")

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
    saved_recipes_count = SavedRecipe.query.filter_by(user_id=user.id).count()
    likes_received = sum(len(recipe.likes) for recipe in own_recipes)

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        own_recipes=own_recipes,
        saved_recipes_count=saved_recipes_count,
        likes_received=likes_received,
    )


@main.route("/profile/<int:user_id>/saved-recipes")
@login_required
def saved_recipes(user_id):
    user = User.query.get_or_404(user_id)

    if user.id != current_user.id:
        abort(403)

    saved_recipes_list = (
        Recipe.query.join(SavedRecipe, SavedRecipe.recipe_id == Recipe.id)
        .filter(SavedRecipe.user_id == user.id)
        .order_by(SavedRecipe.created_at.desc())
        .all()
    )

    return render_template(
        "saved_recipes.html",
        user=user,
        saved_recipes=saved_recipes_list,
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
            (User.username == username) & (User.id != current_user.id)
        ).first()
        email_owner = User.query.filter((User.email == email) & (User.id != current_user.id)).first()

        if not username or not email:
            error = "Username and email are required."
        elif not is_valid_email(email):
            error = "Please enter a real email address."
        elif existing_user:
            error = "That username is already in use."
        elif email_owner:
            error = "That email is already in use."
        else:
            profile_image = save_uploaded_image(profile_image_file)
            if profile_image is None:
                error = "Upload a PNG, JPG, JPEG, GIF, or WEBP image."
            else:
                current_user.username = username
                current_user.bio = bio
                if profile_image:
                    current_user.profile_image = profile_image
                db.session.commit()

                if email != current_user.email:
                    send_email_change_confirmation(current_user, email)
                    success = "Profile saved. Check your new email address to confirm the email change."
                else:
                    return redirect(url_for("main.profile", user_id=current_user.id))

    return render_template(
        "edit_profile.html",
        error=error,
        success=success,
    )
