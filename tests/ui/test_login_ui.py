from playwright.sync_api import Page, expect
from pages.admin_login_page import AdminLoginPage
from conftest import LOGIN_BASE_URL


def test_admin_login_success(page: Page):
    page.goto(LOGIN_BASE_URL)
    AdminLoginPage(page).login("admin", "password")

    expect(page.get_by_role("button", name="Logout")).to_be_visible()


def test_admin_logout_success(page: Page):
    page.goto(LOGIN_BASE_URL)
    AdminLoginPage(page).login("admin", "password")
    AdminLoginPage(page).logout()

    expect(page).to_have_url("http://localhost:3003/")
    expect(page.get_by_role("button", name="Check Availability")).to_be_visible()


def test_admin_login_with_invalid_credentials_shows_error(page: Page):
    page.goto(LOGIN_BASE_URL)
    AdminLoginPage(page).login("wrong_user", "wrong_password")

    error_message = AdminLoginPage(page).get_error_message()
    assert "Invalid credentials" in error_message

    expect(page).to_have_url(LOGIN_BASE_URL)
