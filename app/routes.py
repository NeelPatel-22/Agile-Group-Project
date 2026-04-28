from flask import Blueprint, render_template, request

main = Blueprint('main', __name__)

PROFILE_DATA = {
    "username": "sarahcooks",
    "email": "sarah@example.com",
    "bio": (
        "Passionate home cook who loves sharing easy DIY recipes, healthy meals, "
        "and quick kitchen ideas for busy lifestyles."
    ),
}

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/recipes")
def recipes():
    return render_template("recipes.html")

@main.route("/login")
def login():
    return render_template("login.html")

@main.route("/signup")
def signup():
    return render_template("signup.html")

@main.route("/add-recipe")
def add_recipe():
    return render_template("add_recipe.html")

@main.route("/profile")
def profile():
    return render_template("profile.html", user_profile=PROFILE_DATA)


@main.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    profile_data = PROFILE_DATA.copy()
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        bio = request.form.get("bio", "").strip()

        if not username or not email:
            error = "Username and email are required."
        else:
            PROFILE_DATA["username"] = username
            PROFILE_DATA["email"] = email
            PROFILE_DATA["bio"] = bio
            profile_data = PROFILE_DATA.copy()
            success = "Profile changes saved."
        if error:
            profile_data = {
                "username": username,
                "email": email,
                "bio": bio,
            }

    return render_template(
        "edit_profile.html",
        current_user=profile_data,
        error=error,
        success=success,
    )
