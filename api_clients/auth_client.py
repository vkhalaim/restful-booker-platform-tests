import requests


class AuthApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def login(self, username: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password},
        )
        if response.status_code != 200:
            raise ValueError(f"Login failed with status {response.status_code}: {response.text}")
        token = response.cookies.get("token")
        if not token:
            raise ValueError("Login succeeded but no token cookie was returned")
        return token

    def logout(self, token: str) -> None:
        response = requests.post(
            f"{self.base_url}/logout",
            json={"token": token},
        )
        if response.status_code != 200:
            raise ValueError(f"Logout failed with status {response.status_code}: {response.text}")

    def validate(self, token: str) -> bool:
        response = requests.post(
            f"{self.base_url}/validate",
            json={"token": token},
        )
        return response.status_code == 200
