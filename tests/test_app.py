import re
import unittest
import warnings
from unittest.mock import patch

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="The Query.get\\(\\) method is considered legacy.*")

from app import create_app, db
from app.models import Like, Recipe, SavedRecipe, User


def csrf_from(response):
    match = re.search(rb'name="_csrf_token" value="([^"]+)"', response.data)
    if not match:
        raise AssertionError("CSRF token not found in response")
    return match.group(1).decode()


class RecipeHubTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "UPLOAD_FOLDER": "instance/test_uploads",
                "MAIL_SERVER": None,
            }
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.owner = self.create_user("owner", "owner@example.com")
            self.other = self.create_user("other", "other@example.com")
            self.owner_id = self.owner.id
            self.other_id = self.other.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_user(self, username, email, password="password123"):
        user = User(username=username, email=email, email_confirmed=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def create_recipe(self, user_id=None, title="Lemon Pasta"):
        user_id = user_id or self.owner_id
        recipe = Recipe(
            title=title,
            description="Bright and simple.",
            ingredients="Pasta\nLemon",
            steps="Boil pasta\nAdd lemon",
            user_id=user_id,
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

    def login(self, email="owner@example.com", password="password123"):
        response = self.client.get("/login")
        token = csrf_from(response)
        return self.client.post(
            "/login",
            data={"email": email, "password": password, "_csrf_token": token},
            follow_redirects=True,
        )

    def csrf_header(self):
        with self.client.session_transaction() as session:
            token = session.get("_csrf_token") or "test-csrf-token"
            session["_csrf_token"] = token
        return {"X-CSRFToken": token}


class SecurityTests(RecipeHubTestCase):
    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post("/login", data={"email": "owner@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 400)

    def test_passwords_are_stored_as_hashes(self):
        with self.app.app_context():
            user = User.query.filter_by(email="owner@example.com").first()
            self.assertNotEqual(user.password_hash, "password123")
            self.assertTrue(user.check_password("password123"))

    def test_unconfirmed_users_cannot_login(self):
        with self.app.app_context():
            user = self.create_user("pending", "pending@example.com")
            user.email_confirmed = False
            db.session.commit()

        response = self.login("pending@example.com")
        self.assertIn(b"Please confirm your email", response.data)


class RecipeFeatureTests(RecipeHubTestCase):
    def test_authenticated_user_can_add_recipe(self):
        self.login()
        response = self.client.get("/add-recipe")
        token = csrf_from(response)
        response = self.client.post(
            "/add-recipe",
            data={
                "_csrf_token": token,
                "title": "Tomato Soup",
                "description": "Warm and quick.",
                "ingredients": "Tomato\nStock",
                "steps": "Simmer\nBlend",
                "cook_time": "20",
                "servings": "2",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNotNone(Recipe.query.filter_by(title="Tomato Soup").first())

    def test_recipe_owner_can_edit_recipe(self):
        with self.app.app_context():
            recipe_id = self.create_recipe().id

        self.login()
        response = self.client.get(f"/recipes/{recipe_id}/edit")
        token = csrf_from(response)
        response = self.client.post(
            f"/recipes/{recipe_id}/edit",
            data={
                "_csrf_token": token,
                "title": "Updated Pasta",
                "description": "Updated description.",
                "ingredients": "Pasta",
                "steps": "Cook",
                "cook_time": "15",
                "servings": "2",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.session.get(Recipe, recipe_id).title, "Updated Pasta")

    def test_non_owner_cannot_edit_recipe(self):
        with self.app.app_context():
            recipe_id = self.create_recipe(user_id=self.other_id).id

        self.login()
        response = self.client.get(f"/recipes/{recipe_id}/edit")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete_recipe(self):
        with self.app.app_context():
            recipe_id = self.create_recipe().id

        self.login()
        response = self.client.get(f"/recipes/{recipe_id}/edit")
        token = csrf_from(response)
        response = self.client.post(
            f"/recipes/{recipe_id}/delete",
            data={"_csrf_token": token},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Recipe, recipe_id))

    def test_like_and_save_endpoints_toggle_once_per_user(self):
        with self.app.app_context():
            recipe_id = self.create_recipe().id

        self.login()
        headers = self.csrf_header()
        self.client.post(f"/recipes/{recipe_id}/like", headers=headers)
        self.client.post(f"/recipes/{recipe_id}/save", headers=headers)

        with self.app.app_context():
            self.assertEqual(Like.query.filter_by(recipe_id=recipe_id).count(), 1)
            self.assertEqual(SavedRecipe.query.filter_by(recipe_id=recipe_id).count(), 1)

        self.client.post(f"/recipes/{recipe_id}/like", headers=headers)
        self.client.post(f"/recipes/{recipe_id}/save", headers=headers)

        with self.app.app_context():
            self.assertEqual(Like.query.filter_by(recipe_id=recipe_id).count(), 0)
            self.assertEqual(SavedRecipe.query.filter_by(recipe_id=recipe_id).count(), 0)


class SignupTests(RecipeHubTestCase):
    @patch("app.routes.is_valid_email", return_value=True)
    @patch("app.routes.send_signup_confirmation_email", return_value="http://example.test/confirm")
    def test_signup_creates_pending_confirmation(self, _send_email, _valid_email):
        response = self.client.get("/signup")
        token = csrf_from(response)
        response = self.client.post(
            "/signup",
            data={
                "_csrf_token": token,
                "username": "newcook",
                "email": "newcook@example.com",
                "password": "password123",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Check", response.data)


if __name__ == "__main__":
    unittest.main()
