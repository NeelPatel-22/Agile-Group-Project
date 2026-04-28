from flask import Blueprint, render_template
 
main = Blueprint("main", __name__)
 
 
@main.route("/")
def cover():
    return render_template("cover.html")
 
 
@main.route("/recipes")
def recipes():
    return render_template("recipes.html")
 
 
@main.route("/recipes/<int:recipe_id>")
def recipe_detail(recipe_id):
    return render_template("recipe_detail.html")
 
 
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
    return render_template("profile.html")
 