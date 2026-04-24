# Team Task Breakdown

This project has been restructured to follow the demo app layout while keeping the current HTML and CSS content. The database setup is intentionally minimal for now: it only creates the SQLite file and prints a confirmation message.

Use the tasks below to split the remaining work across team members so everyone can make clear, reviewable commits.

## Current base structure

- `run.py` starts the Flask app.
- `app/__init__.py` contains the app factory and DB path configuration.
- `app/database.py` creates `instance/recipes.db` and prints `DB initialized: ...`.
- `app/routes.py` owns the shared blueprint.
- `app/routes_core.py` contains general page routes.
- `app/routes_auth.py` contains auth page routes.

## Task 1: Add demo-style cover page naming

- Owner focus: landing page alignment
- Files to change:
- `app/routes_core.py`
- `app/templates/cover.html`
- `app/templates/base.html`
- Work:
- Create `app/templates/cover.html` using the current content from `app/templates/index.html`.
- Update the landing route so the app follows the demo naming convention and renders `cover.html`.
- Update navbar links if needed so route names stay correct.

## Task 2: Add edit profile page

- Owner focus: profile management UI
- Files to create or change:
- `app/routes_core.py`
- `app/templates/edit_profile.html`
- `app/static/css/styles.css`
- Work:
- Create an `edit_profile.html` page that matches the current visual style.
- Add a `/edit-profile` route.
- Link the profile page's edit button to the new route.

## Task 3: Add template partials for reusable recipe UI

- Owner focus: reusable frontend components
- Files to create:
- `app/templates/partials/recipe_card.html`
- `app/templates/partials/comment_item.html`
- Files to change:
- `app/templates/recipes.html`
- `app/templates/profile.html`
- Work:
- Move repeated recipe card markup into a partial.
- Create a placeholder comment partial for future backend integration.
- Refactor page templates to include those partials cleanly.

## Task 4: Add models scaffold

- Owner focus: database layer
- Files to create or change:
- `app/models.py`
- `app/__init__.py`
- `requirements.txt`
- Work:
- Add SQLAlchemy model scaffolding for `User` and `Recipe`.
- Do not wire in full business logic yet.
- Update app initialization to register the database extension cleanly.
- Keep the project runnable after the scaffold is added.

## Task 5: Convert auth pages from static forms to working Flask forms

- Owner focus: authentication flow
- Files to change:
- `app/routes_auth.py`
- `app/templates/login.html`
- `app/templates/signup.html`
- Work:
- Add `GET` and `POST` handling for login and signup routes.
- Read form values and show validation messages in the templates.
- Use placeholder success handling for now if the model layer is not ready yet.

## Task 6: Add recipe creation workflow

- Owner focus: recipe submission feature
- Files to change:
- `app/routes_core.py`
- `app/templates/add_recipe.html`
- `app/static/js/script.js`
- Work:
- Turn the add recipe page into a structured form.
- Add client-side enhancement for better UX.
- Add placeholder POST handling that prints submitted values until models are ready.

## Task 7: Improve recipes page into a feed layout

- Owner focus: recipe browsing experience
- Files to change:
- `app/templates/recipes.html`
- `app/static/css/styles.css`
- Work:
- Convert the current single recipe detail-style page into a feed or grid that better matches the user stories.
- Keep the existing design language and CSS variables.
- Prepare the markup so backend data can be looped in later.

## Task 8: Add project documentation for team workflow

- Owner focus: collaboration visibility
- Files to change:
- `README.md`
- Work:
- Document the new project structure.
- Add run instructions.
- Add a simple contribution workflow so each teammate can pick a task, create a branch, open a PR, and request review.
