# RecipeHub

RecipeHub is a Flask web application for sharing DIY recipes. Users can create an account, log in, publish recipes, browse recipes from other users, save favourites, like recipes, comment on recipe pages, and manage their own profile and recipe collection.

## Purpose

The application is designed as a client-server recipe sharing platform for the Agile group project. It demonstrates user authentication, persistent user-generated content, public viewing of other users' data, and interaction features such as comments, likes, saved recipes, and activity updates.

## Design And Use

RecipeHub uses a Flask backend with Jinja templates rendered on the server. The frontend is built with HTML, CSS, JavaScript, Bootstrap, Tailwind CSS, and jQuery. Flask routes handle page rendering, authentication, recipe management, profiles, comments, likes, saves, and activity data. SQLite is accessed through SQLAlchemy, so user accounts and recipe data remain persistent between sessions.

Main user flow:

1. A visitor signs up and confirms their email.
2. The user logs in and creates a recipe.
3. Other logged-in users can browse the shared recipe feed, view recipe details, visit public profiles, comment, like, and save recipes.
4. Recipe owners can edit, archive, unarchive, or delete their own recipes.

## Group Members

| UWA ID | Name | GitHub Username |
| --- | --- | --- |
| 24177393 | Neel Patel | NeelPatel-22 |
| 24574064 | Dhruvik | Dhruvik-uwa |
| 24565676 | Jaylin | jaylin-W |
| 24139958 | Preston | prestonZ211 |

## Main Features

- User signup and login
- Email confirmation before login
- Recipe creation and display
- Recipe image upload support
- User profile page
- Posted recipe management
- Authenticated routing
- SQLite database storage

## Technology Stack

- HTML
- CSS
- JavaScript
- Bootstrap
- Tailwind CSS
- jQuery
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-SocketIO
- SQLite through SQLAlchemy
- AJAX and WebSockets

## Project Structure

```text
app.py                  Flask application entry point
app/__init__.py         App factory, extensions, CSRF, database setup
app/routes.py           Flask routes and SocketIO events
app/models.py           SQLAlchemy models
app/templates/          Jinja HTML templates
app/static/css/         Application stylesheets
app/static/js/          Application JavaScript
app/static/uploads/     Uploaded images
tests/                  Unit and integration tests
tests/selenium/         Optional browser presentation-flow tests
docs/                   Project documentation
```

## Start The Project

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open the app at:

```text
http://127.0.0.1:5001
```

If PowerShell blocks virtual environment activation, run the app directly with:

```powershell
.\.venv\Scripts\python.exe app.py
```

## Environment Variables

Create a `.env` file in the project root. This file is ignored by Git and should not be committed.

```env
SECRET_KEY=replace-with-a-secret-key
SQLALCHEMY_DATABASE_URI=sqlite:///recipes.db
SQLALCHEMY_TRACK_MODIFICATIONS=false
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=5242880
CSRF_PROTECTION_ENABLED=true
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5001

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

For Gmail SMTP, use a Google App Password instead of your normal Gmail password.

## Database

The app uses SQLite through SQLAlchemy. The database file is created automatically inside the `instance` folder when the app starts.

To reset the local database, stop the Flask server and delete:

```text
instance/recipes.db
```

Then run `python app.py` again.

## Run Tests

Run the unit and integration test suite from the project root:

```powershell
python -m unittest discover
```

The repository also includes optional Selenium presentation-flow tests. To run them, start the Flask app, install a compatible browser driver, then run:

```powershell
$env:RECIPEHUB_BASE_URL="http://127.0.0.1:5001"
python -m unittest discover tests/selenium
```

If Selenium or `RECIPEHUB_BASE_URL` is not configured, those browser tests skip cleanly while the backend tests still run.

## Security Notes

The app stores passwords using Werkzeug salted hashes, keeps local secrets in `.env`, and protects POST requests with CSRF tokens. For presentation or deployment, keep `FLASK_DEBUG=false` and use a strong unique `SECRET_KEY`.
