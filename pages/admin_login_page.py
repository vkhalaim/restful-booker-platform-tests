from playwright.sync_api import Page, expect


class AdminLoginPage:
    def __init__(self, page: Page):
        self.page = page

    def login(self, username: str, password: str):
        self.page.get_by_label("Username").fill(username)
        self.page.get_by_label("Password").fill(password)
        self.page.locator("#doLogin").click()

    def logout(self):
        self.page.get_by_role("button", name="Logout").click()

    def get_error_message(self) -> str:
        error_locator = self.page.locator(".alert-danger")
        expect(error_locator).to_have_text("Invalid credentials")
        return error_locator.text_content()
