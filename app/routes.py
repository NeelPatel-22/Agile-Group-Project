import re
import smtplib
import socket
from email.message import EmailMessage

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from . import db
from .models import User
main = Blueprint("main", __name__)

users = [
    {
        "id": 1,
        "name": "Mia Lee",
        "initials": "ML",
        "bio": "Home Cook and Weekend Baker",
        "location": "Perth, Australia",
        "email": "mia.lee@example.com",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
        "followers": 128,
        "likes_received": 342,
    },
    {
        "id": 2,
        "name": "Daniel Wong",
        "initials": "DW",
        "bio": "Food lover sharing quick and easy meals",
        "location": "Sydney, Australia",
        "email": "daniel.wong@example.com",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
        "followers": 96,
        "likes_received": 221,
    },
]

recipes_data = [
    {
        "id": 1,
        "title": "Creamy Roasted Pumpkin Pasta",
        "description": "A silky pumpkin sauce with roasted garlic and crispy sage.",
        "category": "Dinner",
        "cook_time": 35,
        "image_url": "https://images.unsplash.com/photo-1516100882582-96c3a05fe590?auto=format&fit=crop&w=1200&q=80",
        "author_id": 1,
    },
    {
        "id": 2,
        "title": "Berry Yogurt Pancakes",
        "description": "Soft and fluffy pancakes topped with yogurt and fresh berries.",
        "category": "Breakfast",
        "cook_time": 20,
        "image_url": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=1200&q=80",
        "author_id": 1,
    },
    {
        "id": 3,
        "title": "Honey Soy Chicken Bowl",
        "description": "A quick rice bowl with glazed chicken and steamed greens.",
        "category": "Lunch",
        "cook_time": 30,
        "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80",
        "author_id": 2,
    },
]

EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
CONFIRM_EMAIL_SALT = "confirm-email"


def get_user_by_id(user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def get_recipe_by_id(recipe_id):
    for recipe in recipes_data:
        if recipe["id"] == recipe_id:
            return recipe
    return None


def get_recipes_by_user(user_id):
    return [recipe for recipe in recipes_data if recipe["author_id"] == user_id]


def is_valid_email(email):
    if not email or not EMAIL_PATTERN.match(email):
        return False

    domain = email.rsplit("@", 1)[1]

    try:
        import dns.resolver

        dns.resolver.resolve(domain, "MX")
        return True
    except ImportError:
        pass
    except Exception:
        return False

    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=CONFIRM_EMAIL_SALT)


def get_email_from_confirmation_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, salt=CONFIRM_EMAIL_SALT, max_age=max_age)


def send_confirmation_email(user):
    token = generate_confirmation_token(user.email)
    confirmation_url = url_for("main.confirm_email", token=token, _external=True)
    subject = "Confirm your RecipeHub email"
    body = (
        f"Hi {user.username},\n\n"
        "Please confirm your RecipeHub account by opening this link:\n"
        f"{confirmation_url}\n\n"
        "This link expires in 24 hours."
    )

    mail_server = current_app.config.get("MAIL_SERVER")
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    if not mail_server:
        print(f"Email confirmation link for {user.email}: {confirmation_url}")
        return confirmation_url

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = user.email
    message.set_content(body)

    with smtplib.SMTP(mail_server, current_app.config["MAIL_PORT"]) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        if mail_username and mail_password:
            smtp.login(mail_username, mail_password)
        smtp.send_message(message)

    return confirmation_url
 
@main.route("/")
def cover():
    return render_template("cover.html")
 
 
@main.route("/recipes")
def recipes():
    return render_template("recipes.html", recipes=[])
 
 
@main.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        abort(404)
    return render_template("recipe_detail.html", recipe=recipe)
 
 
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
    login_user(user)
    return redirect(url_for("main.recipes"))

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
