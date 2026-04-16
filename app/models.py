from app import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    cooking_time = db.Column(db.String(50), nullable=True)
    servings = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Recipe {self.title}>"