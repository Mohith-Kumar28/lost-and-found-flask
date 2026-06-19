import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "static" / "uploads"
ITEMS_FILE = DATA_DIR / "items.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)


def ensure_storage_exists():
    """Create the folders and JSON file the app needs."""
    DATA_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    if not ITEMS_FILE.exists():
        ITEMS_FILE.write_text("[]", encoding="utf-8")


def load_items():
    """Read saved items from the JSON file."""
    ensure_storage_exists()

    with ITEMS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_items(items):
    """Write the full item list back to the JSON file."""
    with ITEMS_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2)


def allowed_file(filename):
    """Check if the uploaded file looks like an image."""
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def save_uploaded_photo(photo):
    """Save the photo with a unique name so files do not overwrite each other."""
    original_name = secure_filename(photo.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid4().hex}.{extension}"

    photo_path = UPLOADS_DIR / unique_name
    photo.save(photo_path)
    return unique_name


@app.route("/")
def index():
    return render_template("index.html", error=None, form_data={})


@app.route("/submit", methods=["POST"])
def submit_item():
    ensure_storage_exists()

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    found_location = request.form.get("found_location", "").strip()
    found_date = request.form.get("found_date", "").strip()
    photo = request.files.get("photo")

    form_data = {
        "name": name,
        "description": description,
        "found_location": found_location,
        "found_date": found_date,
    }

    # Keep the validation simple so it is easy for students to follow.
    if not name or not description or not found_location or not found_date or not photo:
        error = "Please fill in every field and upload a photo."
        return render_template("index.html", error=error, form_data=form_data), 400

    if not photo.filename or not allowed_file(photo.filename):
        error = "Please upload an image file: png, jpg, jpeg, gif, or webp."
        return render_template("index.html", error=error, form_data=form_data), 400

    items = load_items()
    photo_filename = save_uploaded_photo(photo)

    item = {
        "id": uuid4().hex,
        "name": name,
        "description": description,
        "found_location": found_location,
        "found_date": found_date,
        "photo_filename": photo_filename,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    items.insert(0, item)
    save_items(items)

    return redirect(url_for("items", added="1"))


@app.route("/items")
def items():
    saved_items = load_items()
    just_added = request.args.get("added") == "1"
    return render_template("items.html", items=saved_items, just_added=just_added)


if __name__ == "__main__":
    ensure_storage_exists()
    app.run(debug=True)
