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


def build_recipe_view(recipe):
    author = get_user_by_id(recipe["author_id"])
    recipe_view = recipe.copy()
    recipe_view["author"] = author
    recipe_view.setdefault("servings", 4)
    recipe_view.setdefault("ingredients", ["Fresh ingredients", "Seasoning", "Olive oil"])
    recipe_view.setdefault("overview", recipe["description"])
    recipe_view.setdefault("difficulty", "Easy")
    recipe_view.setdefault("best_for", recipe["category"])
    recipe_view.setdefault("cuisine", "Home-style")
    recipe_view.setdefault(
        "steps",
        [
            {
                "title": "Prepare ingredients",
                "description": "Gather and prepare all ingredients before cooking.",
            },
            {
                "title": "Cook",
                "description": "Follow the recipe method and cook until ready.",
            },
            {
                "title": "Serve",
                "description": "Plate the dish and serve while fresh.",
            },
        ],
    )
    return recipe_view


def get_recipe_by_id(recipe_id):
    for recipe in recipes_data:
        if recipe["id"] == recipe_id:
            return build_recipe_view(recipe)
    return None


def get_recipes_by_user(user_id):
    return [build_recipe_view(recipe) for recipe in recipes_data if recipe["author_id"] == user_id]


def get_more_recipes_by_author(author_id, current_recipe_id):
    return [
        build_recipe_view(recipe)
        for recipe in recipes_data
        if recipe["author_id"] == author_id and recipe["id"] != current_recipe_id
    ]
