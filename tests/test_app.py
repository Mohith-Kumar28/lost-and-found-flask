import importlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load_fresh_app_module():
    """Reload the app after changing environment variables."""
    if "app" in sys.modules:
        return importlib.reload(sys.modules["app"])

    return importlib.import_module("app")


class LostFoundAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)

        self.original_database_url = os.environ.get("DATABASE_URL")
        self.original_cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
        self.original_api_key = os.environ.get("CLOUDINARY_API_KEY")
        self.original_api_secret = os.environ.get("CLOUDINARY_API_SECRET")
        self.original_openai_api_key = os.environ.get("OPENAI_API_KEY")

        os.environ["DATABASE_URL"] = f"sqlite:///{temp_path / 'test.db'}"
        os.environ["CLOUDINARY_CLOUD_NAME"] = "demo-cloud"
        os.environ["CLOUDINARY_API_KEY"] = "demo-key"
        os.environ["CLOUDINARY_API_SECRET"] = "demo-secret"
        os.environ["OPENAI_API_KEY"] = "demo-openai-key"

        self.app_module = load_fresh_app_module()
        self.app_module.app.config["TESTING"] = True
        self.client = self.app_module.app.test_client()
        self.upload_patcher = mock.patch.object(
            self.app_module.cloudinary.uploader,
            "upload",
            return_value={"secure_url": "https://example.com/item.png"},
        )
        self.upload_patcher.start()

    def tearDown(self):
        self.upload_patcher.stop()

        if self.original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = self.original_database_url

        if self.original_cloud_name is None:
            os.environ.pop("CLOUDINARY_CLOUD_NAME", None)
        else:
            os.environ["CLOUDINARY_CLOUD_NAME"] = self.original_cloud_name

        if self.original_api_key is None:
            os.environ.pop("CLOUDINARY_API_KEY", None)
        else:
            os.environ["CLOUDINARY_API_KEY"] = self.original_api_key

        if self.original_api_secret is None:
            os.environ.pop("CLOUDINARY_API_SECRET", None)
        else:
            os.environ["CLOUDINARY_API_SECRET"] = self.original_api_secret

        if self.original_openai_api_key is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = self.original_openai_api_key

        self.temp_dir.cleanup()

    def submit_item(self, name, description, found_location, found_date, contact):
        """Helper to keep the test code short and easy to read."""
        return self.client.post(
            "/submit",
            data={
                "name": name,
                "description": description,
                "found_location": found_location,
                "found_date": found_date,
                "contact": contact,
                "photo": (io.BytesIO(b"fake image bytes"), "item.png"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Found Item Form", response.data)

    def test_lost_report_page_loads(self):
        response = self.client.get("/lost-report")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lost Item Form", response.data)

    def test_submit_item_saves_in_database(self):
        response = self.submit_item(
            "Blue notebook",
            "Blue notebook with science notes inside.",
            "Room 12",
            "2026-06-19",
            "9876543210",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Blue notebook", response.data)

        with self.app_module.app.app_context():
            saved_items = self.app_module.Item.query.all()
            self.assertEqual(len(saved_items), 1)
            self.assertEqual(saved_items[0].found_location, "Room 12")
            self.assertEqual(saved_items[0].contact, "9876543210")
            self.assertEqual(saved_items[0].photo_url, "https://example.com/item.png")

    def test_search_and_filter_work_on_home_page(self):
        self.submit_item(
            "Blue notebook",
            "Science notes inside.",
            "Room 12",
            "2026-06-19",
            "blue@example.com",
        )
        self.submit_item(
            "Red bottle",
            "Sports bottle.",
            "Library",
            "2026-06-20",
            "9999999999",
        )

        response = self.client.get(
            "/items?search=blue@example.com&location=Room+12&found_date=2026-06-19"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Blue notebook", response.data)
        self.assertNotIn(b"Red bottle", response.data)

    def test_edit_and_delete_routes_work(self):
        self.submit_item(
            "Blue notebook",
            "Science notes inside.",
            "Room 12",
            "2026-06-19",
            "9876543210",
        )

        with self.app_module.app.app_context():
            item = self.app_module.Item.query.first()
            item_id = item.id

        edit_response = self.client.post(
            f"/items/{item_id}/edit",
            data={
                "name": "Green notebook",
                "description": "Updated description.",
                "found_location": "Lab",
                "found_date": "2026-06-21",
                "contact": "green@example.com",
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertEqual(edit_response.status_code, 200)
        self.assertIn(b"Green notebook", edit_response.data)

        with self.app_module.app.app_context():
            edited_item = self.app_module.db.session.get(self.app_module.Item, item_id)
            self.assertEqual(edited_item.name, "Green notebook")
            self.assertEqual(edited_item.found_location, "Lab")
            self.assertEqual(edited_item.contact, "green@example.com")

        delete_response = self.client.post(
            f"/items/{item_id}/delete",
            follow_redirects=True,
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertNotIn(b"Green notebook", delete_response.data)

        with self.app_module.app.app_context():
            self.assertEqual(self.app_module.Item.query.count(), 0)

    def test_autofill_route_returns_ai_suggestions(self):
        with mock.patch.object(
            self.app_module,
            "analyze_image_with_ai",
            return_value={
                "name": "Blue water bottle",
                "description": "A blue bottle with a black cap.",
                "found_location": "",
            },
        ):
            response = self.client.post(
                "/autofill",
                data={"photo": (io.BytesIO(b"fake image bytes"), "item.png")},
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["name"], "Blue water bottle")
        self.assertEqual(json_data["photo_url"], "https://example.com/item.png")

    def test_submit_item_can_use_ai_photo_url(self):
        response = self.client.post(
            "/submit",
            data={
                "name": "AI bottle",
                "description": "AI found a blue bottle in the image.",
                "found_location": "Hallway",
                "found_date": "2026-06-22",
                "contact": "kid@example.com",
                "photo_url": "https://example.com/ai-item.png",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI bottle", response.data)

        with self.app_module.app.app_context():
            saved_item = self.app_module.Item.query.first()
            self.assertEqual(saved_item.photo_url, "https://example.com/ai-item.png")
            self.assertEqual(saved_item.contact, "kid@example.com")

    def test_lost_report_matches_a_similar_found_item(self):
        self.submit_item(
            "Black water bottle",
            "Black bottle with a sticker on it.",
            "Library",
            "2026-06-20",
            "9876543210",
        )

        with mock.patch.object(
            self.app_module,
            "normalize_lost_report_with_ai",
            return_value={
                "name": "Black water bottle",
                "normalized_description": "Black bottle with sticker",
                "category": "bottle",
                "color": "black",
                "keywords": ["black", "bottle", "sticker", "library"],
            },
        ):
            response = self.client.post(
                "/lost-report/matches",
                data={
                    "name": "Water bottle",
                    "description": "I lost my black bottle with a sticker.",
                    "lost_location": "Library",
                    "lost_date": "2026-06-20",
                    "contact": "kid@example.com",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Black water bottle", response.data)
        self.assertIn(b"Strong match", response.data)

    def test_lost_report_shows_empty_state_when_no_match_exists(self):
        response = self.client.post(
            "/lost-report/matches",
            data={
                "name": "Green pencil box",
                "description": "A green pencil box with cartoon stickers.",
                "lost_location": "Classroom",
                "lost_date": "2026-06-25",
                "contact": "kid@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No strong matches yet", response.data)


if __name__ == "__main__":
    unittest.main()
