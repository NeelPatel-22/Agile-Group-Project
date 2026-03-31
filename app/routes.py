from flask import Blueprint, render_template

main = Blueprint('main', __name__)

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
    return render_template("profile.html")