import io
import json
import tempfile
import unittest
from pathlib import Path

import app as lost_found_app


class LostFoundAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)

        self.original_data_dir = lost_found_app.DATA_DIR
        self.original_uploads_dir = lost_found_app.UPLOADS_DIR
        self.original_items_file = lost_found_app.ITEMS_FILE

        lost_found_app.DATA_DIR = temp_path / "data"
        lost_found_app.UPLOADS_DIR = temp_path / "static" / "uploads"
        lost_found_app.ITEMS_FILE = lost_found_app.DATA_DIR / "items.json"

        lost_found_app.app.config["TESTING"] = True
        self.client = lost_found_app.app.test_client()

    def tearDown(self):
        lost_found_app.DATA_DIR = self.original_data_dir
        lost_found_app.UPLOADS_DIR = self.original_uploads_dir
        lost_found_app.ITEMS_FILE = self.original_items_file
        self.temp_dir.cleanup()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Found Item Form", response.data)

    def test_submit_item_saves_json_and_upload(self):
        response = self.client.post(
            "/submit",
            data={
                "name": "Blue notebook",
                "description": "Blue notebook with science notes inside.",
                "found_location": "Room 12",
                "found_date": "2026-06-19",
                "photo": (io.BytesIO(b"fake image bytes"), "notebook.png"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Blue notebook", response.data)
        self.assertTrue(lost_found_app.ITEMS_FILE.exists())

        saved_items = json.loads(lost_found_app.ITEMS_FILE.read_text(encoding="utf-8"))
        self.assertEqual(len(saved_items), 1)
        self.assertEqual(saved_items[0]["found_location"], "Room 12")

        uploaded_files = list(lost_found_app.UPLOADS_DIR.glob("*"))
        self.assertEqual(len(uploaded_files), 1)


if __name__ == "__main__":
    unittest.main()
