import requests


class BookingApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create_booking(self, booking_payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/",
            json=booking_payload,
        )
        if response.status_code != 201:
            raise ValueError(
                f"Booking creation failed with status {response.status_code}: {response.text}"
            )
        return response.json()

    def get_booking(self, booking_id: int, token: str) -> dict:
        response = requests.get(
            f"{self.base_url}/{booking_id}",
            cookies={"token": token}
            )
        if response.status_code != 200:
            raise ValueError(
                f"Get booking failed with status {response.status_code}: {response.text}"
            )
        return response.json()

    def update_booking(self, booking_id: int, booking_payload: dict, token: str) -> dict:
        response = requests.put(
            f"{self.base_url}/{booking_id}",
            cookies={"token": token},
            json=booking_payload,
        )
        if response.status_code != 200:
            raise ValueError(
                f"Update booking failed with status {response.status_code}: {response.text}"
            )
        return response.json()

    def delete_booking(self, booking_id: int, token: str) -> None:
        response = requests.delete(
            f"{self.base_url}/{booking_id}",
            cookies={"token": token},
        )
        if response.status_code != 202:
            raise ValueError(
                f"Delete booking failed with status {response.status_code}: {response.text}"
            )
