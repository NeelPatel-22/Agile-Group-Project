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
        "overview": "This cozy pasta is easy to prepare and perfect for busy weeknights.",
        "category": "Dinner",
        "cook_time": 35,
        "servings": 4,
        "difficulty": "Beginner Friendly",
        "best_for": "Family Dinner",
        "cuisine": "Italian-inspired",
        "image_url": "https://images.unsplash.com/photo-1516100882582-96c3a05fe590?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "300g pasta of your choice",
            "2 cups roasted pumpkin cubes",
            "4 cloves roasted garlic",
            "3/4 cup cooking cream",
            "1/3 cup grated parmesan",
            "8 sage leaves",
            "1 tbsp olive oil",
            "Salt and black pepper",
        ],
        "steps": [
            {
                "title": "Roast the pumpkin and garlic",
                "description": "Toss pumpkin cubes and garlic with olive oil, then roast until soft and caramelised.",
            },
            {
                "title": "Blend a smooth sauce",
                "description": "Blend roasted pumpkin, garlic, cream, parmesan, and a splash of pasta water until smooth.",
            },
            {
                "title": "Finish with pasta",
                "description": "Coat cooked pasta in the sauce and top with crispy sage before serving.",
            },
        ],
        "author_id": 1,
    },
    {
        "id": 2,
        "title": "Berry Yogurt Pancakes",
        "description": "Soft and fluffy pancakes topped with yogurt and fresh berries.",
        "overview": "A bright and easy breakfast recipe that works well for weekends.",
        "category": "Breakfast",
        "cook_time": 20,
        "servings": 2,
        "difficulty": "Easy",
        "best_for": "Weekend Brunch",
        "cuisine": "Modern Australian",
        "image_url": "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "1 cup flour",
            "1 egg",
            "3/4 cup milk",
            "1 tbsp sugar",
            "1 tsp baking powder",
            "Greek yogurt",
            "Fresh berries",
        ],
        "steps": [
            {
                "title": "Prepare the batter",
                "description": "Mix flour, sugar, baking powder, egg, and milk until smooth.",
            },
            {
                "title": "Cook the pancakes",
                "description": "Pour batter into a hot pan and cook both sides until golden.",
            },
            {
                "title": "Serve",
                "description": "Top with yogurt and fresh berries before serving.",
            },
        ],
        "author_id": 1,
    },
    {
        "id": 3,
        "title": "Honey Soy Chicken Bowl",
        "description": "A quick rice bowl with glazed chicken and steamed greens.",
        "overview": "Balanced, filling, and ideal for lunch or dinner meal prep.",
        "category": "Lunch",
        "cook_time": 30,
        "servings": 3,
        "difficulty": "Medium",
        "best_for": "Meal Prep",
        "cuisine": "Asian-inspired",
        "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "2 chicken breasts",
            "2 tbsp soy sauce",
            "1 tbsp honey",
            "2 cups cooked rice",
            "Broccoli",
            "Carrot",
        ],
        "steps": [
            {
                "title": "Cook the chicken",
                "description": "Pan-fry sliced chicken until browned and cooked through.",
            },
            {
                "title": "Add the glaze",
                "description": "Stir in soy sauce and honey and cook until glossy.",
            },
            {
                "title": "Assemble the bowl",
                "description": "Serve over rice with steamed vegetables.",
            },
        ],
        "author_id": 2,
    },
]


def get_user_by_id(user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def attach_author(recipe):
    recipe_copy = recipe.copy()
    recipe_copy["author"] = get_user_by_id(recipe["author_id"])
    return recipe_copy


def get_recipe_by_id(recipe_id):
    for recipe in recipes_data:
        if recipe["id"] == recipe_id:
            return recipe
    return None


def get_recipe_with_author(recipe_id):
    recipe = get_recipe_by_id(recipe_id)
    if recipe:
        return attach_author(recipe)
    return None


def get_recipes_by_user(user_id):
    return [attach_author(recipe) for recipe in recipes_data if recipe["author_id"] == user_id]


def recipe_to_form(recipe):
    form_recipe = recipe.copy()
    form_recipe.setdefault("why_people_love_it", "")
    form_recipe.setdefault("flavor_notes", "")
    form_recipe.setdefault("skill_level", form_recipe.get("difficulty", ""))
    form_recipe.setdefault("pair_with", "")
    form_recipe.setdefault("spice_level", "")
    form_recipe.setdefault("dietary_cautions", "")
    form_recipe["ingredients"] = "\n".join(recipe.get("ingredients", []))
    form_recipe["steps"] = "\n".join(
        step["description"] if isinstance(step, dict) else str(step)
        for step in recipe.get("steps", [])
    )
    return form_recipe


@main.route("/")
def cover():
    return render_template("cover.html")


@main.route("/recipes")
def recipes():
    recipes = [attach_author(recipe) for recipe in recipes_data]
    return render_template("recipes.html", recipes=recipes)


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
