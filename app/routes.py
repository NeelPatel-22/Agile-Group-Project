from flask import Blueprint, render_template, request, abort

main = Blueprint("main", __name__)

# Dummy users
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
    {
        "id": 3,
        "name": "Sophie Tan",
        "initials": "ST",
        "bio": "Brunch Enthusiast and Recipe Sharer",
        "location": "Sydney, Australia",
        "email": "sophie.tan@example.com",
        "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&q=80",
        "followers": 156,
        "likes_received": 401,
    },
    {
        "id": 4,
        "name": "Noah Carter",
        "initials": "NC",
        "bio": "Simple Meals Maker and Coffee Lover",
        "location": "Brisbane, Australia",
        "email": "noah.carter@example.com",
        "avatar_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
        "followers": 89,
        "likes_received": 267,
    },
]

# Dummy recipes
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
    {
        "id": 4,
        "title": "Avocado Toast with Poached Egg",
        "description": "Crunchy toast topped with smashed avocado and a perfectly poached egg.",
        "overview": "A fresh and satisfying breakfast that is quick to prepare.",
        "category": "Breakfast",
        "cook_time": 15,
        "servings": 1,
        "difficulty": "Easy",
        "best_for": "Quick Morning Meal",
        "cuisine": "Australian Cafe Style",
        "image_url": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "1 egg",
            "1 tsp lemon juice",
            "Salt",
            "Black pepper",
            "Chili flakes",
        ],
        "steps": [
            {
                "title": "Toast the bread",
                "description": "Toast the sourdough slices until crisp and golden.",
            },
            {
                "title": "Prepare the topping",
                "description": "Mash avocado with lemon juice, salt, and pepper.",
            },
            {
                "title": "Poach the egg",
                "description": "Poach the egg in simmering water until the white is set.",
            },
            {
                "title": "Assemble",
                "description": "Spread avocado on toast, place the egg on top, and finish with chili flakes.",
            },
        ],
        "author_id": 3,
    },
    {
        "id": 5,
        "title": "Chicken Caesar Wrap",
        "description": "Tender chicken, crisp lettuce, and Caesar dressing wrapped in a soft tortilla.",
        "overview": "A simple lunch recipe that is easy to pack and enjoy on the go.",
        "category": "Lunch",
        "cook_time": 25,
        "servings": 2,
        "difficulty": "Easy",
        "best_for": "Work Lunch",
        "cuisine": "Western",
        "image_url": "https://images.unsplash.com/photo-1539252554453-80ab65ce3586?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "2 tortilla wraps",
            "1 chicken breast",
            "2 cups romaine lettuce",
            "2 tbsp Caesar dressing",
            "2 tbsp grated parmesan",
            "Salt",
            "Black pepper",
        ],
        "steps": [
            {
                "title": "Cook the chicken",
                "description": "Season and pan-fry the chicken breast until cooked through, then slice.",
            },
            {
                "title": "Prepare the filling",
                "description": "Toss lettuce with Caesar dressing and parmesan.",
            },
            {
                "title": "Wrap it up",
                "description": "Fill each tortilla with chicken and lettuce mixture, then roll tightly.",
            },
        ],
        "author_id": 3,
    },
    {
        "id": 6,
        "title": "Creamy Mushroom Pasta",
        "description": "Rich and creamy pasta with sauteed mushrooms and parmesan.",
        "overview": "A comforting dinner recipe perfect for busy evenings.",
        "category": "Dinner",
        "cook_time": 30,
        "servings": 2,
        "difficulty": "Medium",
        "best_for": "Weeknight Dinner",
        "cuisine": "Italian Inspired",
        "image_url": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=1200&q=80",
        "ingredients": [
            "200g fettuccine",
            "200g mushrooms",
            "1 clove garlic",
            "1/2 cup cream",
            "2 tbsp parmesan",
            "1 tbsp olive oil",
            "Salt",
            "Black pepper",
        ],
        "steps": [
            {
                "title": "Cook the pasta",
                "description": "Boil the fettuccine until al dente and reserve a little pasta water.",
            },
            {
                "title": "Cook the mushrooms",
                "description": "Saute mushrooms and garlic in olive oil until soft and golden.",
            },
            {
                "title": "Make the sauce",
                "description": "Add cream and parmesan, then stir until smooth.",
            },
            {
                "title": "Combine and serve",
                "description": "Toss pasta with the sauce, adjust seasoning, and serve warm.",
            },
        ],
        "author_id": 4,
    },
]


def get_user_by_id(user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def attach_author(recipe):
    recipe_copy = recipe.copy()
    author = get_user_by_id(recipe["author_id"])
    recipe_copy["author"] = author
    return recipe_copy


def get_recipe_by_id(recipe_id):
    for recipe in recipes_data:
        if recipe["id"] == recipe_id:
            return attach_author(recipe)
    return None


def get_recipes_by_user(user_id):
    return [attach_author(recipe) for recipe in recipes_data if recipe["author_id"] == user_id]


@main.route("/")
def cover():
    return render_template("cover.html")


@main.route("/recipes")
def recipes():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip().lower()

    filtered_recipes = [attach_author(recipe) for recipe in recipes_data]

    if query:
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if query in recipe["title"].lower()
            or query in recipe["description"].lower()
            or query in recipe["category"].lower()
        ]

    if category:
        filtered_recipes = [
            recipe for recipe in filtered_recipes
            if recipe["category"].lower() == category
        ]

    return render_template("recipes.html", recipes=filtered_recipes)


@main.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        abort(404)

    more_recipes = [
        attach_author(r)
        for r in recipes_data
        if r["author_id"] == recipe["author"]["id"] and r["id"] != recipe_id
    ]

    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        more_recipes=more_recipes,
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
            form_user.update({
                "name": username,
                "email": email,
                "bio": bio,
            })
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
