from flask import Blueprint, redirect, render_template, request, url_for

from app import db
from app.models import Recipe

recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.route("/recipes")
def recipes_page():
    return render_template("recipes.html")


@recipes_bp.route("/add-recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        ingredients = request.form.get("ingredients")
        steps = request.form.get("steps")
        category = request.form.get("category")
        cooking_time = request.form.get("cooking_time")
        servings = request.form.get("servings")

        new_recipe = Recipe(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            category=category,
            cooking_time=cooking_time,
            servings=servings,
        )

        db.session.add(new_recipe)
        db.session.commit()

        return redirect(url_for("recipes.recipes_page"))

    return render_template("add_recipe.html")
