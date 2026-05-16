# Agile-Group-Project

This is a Flask web application for the RecipeHub group project.

## Start the Project

Run these commands from the project root:

```powershell
cd D:\Semester-4\Agile-Group-Project
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

The app uses SQLite. The database file is created automatically inside the `instance` folder when the app starts.

To reset the local database, stop the Flask server and delete:

```text
instance/recipes.db
```

Then run `python app.py` again.

## Testing

Run the unit and integration test suite from the project root:

```powershell
python -m unittest discover
```

The repository also includes Selenium presentation-flow tests. To run them, start the Flask app, install a compatible browser driver, then run:

```powershell
$env:RECIPEHUB_BASE_URL="http://127.0.0.1:5001"
python -m unittest discover tests/selenium
```

If Selenium or `RECIPEHUB_BASE_URL` is not configured, those browser tests skip cleanly while the backend tests still run.

## Security Notes

The app stores passwords using Werkzeug salted hashes, keeps local secrets in `.env`, and protects POST requests with CSRF tokens. For presentation or deployment, keep `FLASK_DEBUG=false` and use a strong unique `SECRET_KEY`.
