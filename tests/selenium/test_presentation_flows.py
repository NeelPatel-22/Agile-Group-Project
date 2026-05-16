import os
import unittest

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:  # pragma: no cover - documents the optional browser suite.
    webdriver = None


@unittest.skipIf(webdriver is None, "selenium is not installed")
@unittest.skipUnless(os.environ.get("RECIPEHUB_BASE_URL"), "set RECIPEHUB_BASE_URL to run live Selenium tests")
class PresentationFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = os.environ["RECIPEHUB_BASE_URL"].rstrip("/")
        cls.browser = webdriver.Chrome()
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def open_page(self, path):
        self.browser.get(f"{self.base_url}{path}")

    def test_01_cover_page_has_clear_navigation(self):
        self.open_page("/")
        self.assertIn("RecipeHub", self.browser.title)
        self.assertTrue(self.browser.find_element(By.LINK_TEXT, "Login").is_displayed())
        self.assertTrue(self.browser.find_element(By.LINK_TEXT, "Sign up").is_displayed())

    def test_02_login_page_validates_required_fields(self):
        self.open_page("/login")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        email = self.browser.find_element(By.ID, "login-email")
        self.assertFalse(email.get_attribute("validationMessage") == "")

    def test_03_signup_page_has_expected_account_fields(self):
        self.open_page("/signup")
        self.assertTrue(self.browser.find_element(By.ID, "signup-username").is_displayed())
        self.assertTrue(self.browser.find_element(By.ID, "signup-email").is_displayed())
        self.assertTrue(self.browser.find_element(By.ID, "signup-password").is_displayed())

    def test_04_recipe_feed_requires_login(self):
        self.open_page("/recipes")
        self.wait.until(EC.presence_of_element_located((By.ID, "login-email")))
        self.assertIn("/login", self.browser.current_url)

    def test_05_forgot_password_flow_renders_secure_form(self):
        self.open_page("/forgot-password")
        self.assertTrue(self.browser.find_element(By.ID, "forgot-email").is_displayed())
        self.assertIsNotNone(self.browser.find_element(By.NAME, "_csrf_token"))
