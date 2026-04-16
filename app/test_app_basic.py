import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models


class TestThreatWatchBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_incidents_list(self):
        response = self.client.get("/api/v1/incidents/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_ctf_challenges_list(self):
        response = self.client.get("/ctf/challenges")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_signup_login_me(self):
        email = f"testuser_{uuid4().hex}@example.com"
        payload = {
            "username": "testuser",
            "email": email,
            "password": "testpassword",
        }
        signup_response = self.client.post("/api/v1/signup", json=payload)
        self.assertEqual(signup_response.status_code, 200)

        login_data = {
            "username": email,
            "password": "testpassword",
        }
        login_response = self.client.post(
            "/api/v1/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json().get("access_token")
        self.assertIsInstance(token, str)

        me_response = self.client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_response.status_code, 200)
        me_data = me_response.json()
        self.assertEqual(me_data.get("email"), email)

    def test_admin_endpoints_require_admin(self):
        email = f"admin_{uuid4().hex}@example.com"
        payload = {
            "username": "adminuser",
            "email": email,
            "password": "adminpassword",
        }
        signup_response = self.client.post("/api/v1/signup", json=payload)
        self.assertEqual(signup_response.status_code, 200)

        db = SessionLocal()
        user = db.query(models.User).filter(models.User.email == email).first()
        self.assertIsNotNone(user)
        user.is_admin = True
        db.add(user)
        db.commit()
        db.close()

        login_data = {
            "username": email,
            "password": "adminpassword",
        }
        login_response = self.client.post(
            "/api/v1/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json().get("access_token")
        self.assertIsInstance(token, str)

        headers = {"Authorization": f"Bearer {token}"}

        reports_response = self.client.get("/api/v1/admin/ctf/reports", headers=headers)
        self.assertEqual(reports_response.status_code, 200)
        reports_data = reports_response.json()
        self.assertIsInstance(reports_data, list)

        pending_response = self.client.get(
            "/api/v1/admin/contributions/pending",
            headers=headers,
        )
        self.assertEqual(pending_response.status_code, 200)
        pending_data = pending_response.json()
        self.assertIsInstance(pending_data, list)

        stats_response = self.client.get(
            "/api/v1/admin/contributions/stats",
            headers=headers,
        )
        self.assertEqual(stats_response.status_code, 200)
        stats_data = stats_response.json()
        self.assertIsInstance(stats_data, list)


if __name__ == "__main__":
    unittest.main()

