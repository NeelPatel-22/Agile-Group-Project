from flask import Blueprint, abort, render_template, request

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


@main.route("/")
def cover():
    return render_template("cover.html")


@main.route("/recipes")
def recipes():
    return render_template("recipes.html")


@main.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        abort(404)
    return render_template("recipe_detail.html", recipe=recipe)


@main.route("/login")
def login():
    return render_template("login.html")


@main.route("/signup")
def signup():
    return render_template("signup.html")


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
