# RecipeHub

A Flask recipe-sharing website built with:

- HTML
- CSS
- JavaScript
- Bootstrap
- jQuery
- Flask
- Flask-Login
- SQLite with SQLAlchemy
- AJAX and WebSockets

## Features

- Cover page / landing page
- Login and signup
- Recipe feed with search
- Like, save, and comment on recipes
- Profile page for posting recipes
- Saved recipes section
- Hide/show comments on your own recipes
- Live updates for recipe interactions

## Run the project

1. Create a virtual environment:

```powershell
python -m venv .venv
```

2. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Start the app:

```powershell
python run.py
```

5. Open the browser at:

```text
http://127.0.0.1:5000
```

## Project structure

```text
app/
|-- static/
|   |-- css/
|   |   |-- home.css
|   |   |-- profile.css
|   |   `-- style.css
|   |-- images/
|   |-- js/
|   |   `-- main.js
|   `-- uploads/
|-- templates/
|   |-- partials/
|   |-- add_recipe.html
|   |-- base.html
|   |-- cover.html
|   |-- edit_profile.html
|   |-- login.html
|   |-- profile.html
|   |-- recipes.html
|   `-- signup.html
|-- __init__.py
|-- models.py
`-- routes.py
```

## Notes

- Recipe images currently use image URLs.
- The secret key in `app/__init__.py` should be changed before production use.
- Bootstrap, jQuery, Socket.IO, Google Fonts, and demo images are loaded from CDNs.
