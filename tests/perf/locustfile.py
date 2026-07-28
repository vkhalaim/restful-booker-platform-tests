from locust import HttpUser, task, between
import random
import uuid
from datetime import date, timedelta


class BookingUser(HttpUser):
    host = "http://localhost:3000/booking"
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post(
            "http://localhost:3004/auth/login",
            json={"username": "admin", "password": "password"},
            name="/auth/login",  # группировка в отчёте, чтобы не мешал полный URL
        )
        self.token = response.cookies.get("token")

    @task(3)
    def get_all_bookings(self):
        self.client.get("/", cookies={"token": self.token})

    @task(1)
    def create_booking(self):
        start_day = random.randint(1, 3650)
        duration = random.randint(1, 14)
        checkin = date.today() + timedelta(days=start_day)
        checkout = checkin + timedelta(days=duration)

        with self.client.post(
            "/",
            json={
                "roomid": random.choice([1, 2, 3]),
                "firstname": "Load",
                "lastname": f"Test{uuid.uuid4().hex[:6]}",
                "depositpaid": True,
                "email": f"load{uuid.uuid4().hex[:6]}@test.com",
                "phone": "12345678901",
                "bookingdates": {"checkin": str(checkin), "checkout": str(checkout)},
            },
            catch_response=True,
        ) as response:
            if response.status_code == 409:
                response.success()  # expected behavior with dates collisions
            elif response.status_code != 201:
                response.failure(f"Unexpected status: {response.status_code}")