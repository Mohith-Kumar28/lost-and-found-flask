import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import or_


BASE_DIR = Path(__file__).resolve().parent
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

load_dotenv()

app = Flask(__name__)
database_url = os.environ.get("DATABASE_URL", "").strip()

if not database_url:
    raise RuntimeError("Please add DATABASE_URL to your .env file.")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Item(db.Model):
    """One found item."""

    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    found_location = db.Column(db.String(120), nullable=False, index=True)
    found_date = db.Column(db.String(10), nullable=False, index=True)
    photo_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


def setup_app():
    """Create the database table we need."""
    with app.app_context():
        db.create_all()


def cloudinary_ready():
    """Check if Cloudinary keys exist."""
    return bool(
        os.environ.get("CLOUDINARY_CLOUD_NAME")
        and os.environ.get("CLOUDINARY_API_KEY")
        and os.environ.get("CLOUDINARY_API_SECRET")
    )


def allowed_file(filename):
    """Check if the uploaded file looks like an image."""
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def upload_photo(photo):
    """Upload the image to Cloudinary and return the image URL."""
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )
    result = cloudinary.uploader.upload(
        photo,
        folder="lost-found-flask",
        public_id=f"item-{uuid4().hex}",
        resource_type="image",
    )
    return result["secure_url"]


def render_items_page(message=""):
    """Render the items page with search and filters."""
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    found_date = request.args.get("found_date", "").strip()

    items_query = Item.query.order_by(Item.created_at.desc())

    if search:
        like_text = f"%{search}%"
        items_query = items_query.filter(
            or_(
                Item.name.ilike(like_text),
                Item.description.ilike(like_text),
                Item.found_location.ilike(like_text),
            )
        )

    if location:
        items_query = items_query.filter_by(found_location=location)

    if found_date:
        items_query = items_query.filter_by(found_date=found_date)

    locations = db.session.query(Item.found_location).distinct().order_by(Item.found_location).all()

    return render_template(
        "items.html",
        items=items_query.all(),
        filters={"search": search, "location": location, "found_date": found_date},
        locations=[row[0] for row in locations],
        message=message,
    )


@app.route("/")
def index():
    return render_template(
        "index.html",
        error=None,
        form_data={},
        using_cloudinary=cloudinary_ready(),
    )


@app.route("/submit", methods=["POST"])
def submit_item():
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

    # Simple validation for beginners.
    if not name or not description or not found_location or not found_date or not photo:
        return (
            render_template(
                "index.html",
                error="Please fill every field and upload a photo.",
                form_data=form_data,
                using_cloudinary=cloudinary_ready(),
            ),
            400,
        )

    if not photo.filename or not allowed_file(photo.filename):
        return (
            render_template(
                "index.html",
                error="Please upload a valid image.",
                form_data=form_data,
                using_cloudinary=cloudinary_ready(),
            ),
            400,
        )

    if not cloudinary_ready():
        return (
            render_template(
                "index.html",
                error="Please add Cloudinary keys first.",
                form_data=form_data,
                using_cloudinary=cloudinary_ready(),
            ),
            400,
        )

    item = Item(
        name=name,
        description=description,
        found_location=found_location,
        found_date=found_date,
        photo_url=upload_photo(photo),
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("items", added="1"))


@app.route("/items")
def items():
    if request.args.get("added") == "1":
        return render_items_page("Item saved successfully.")

    if request.args.get("updated") == "1":
        return render_items_page("Item updated successfully.")

    if request.args.get("deleted") == "1":
        return render_items_page("Item deleted successfully.")

    return render_items_page()


@app.route("/items/<item_id>/edit", methods=["POST"])
def edit_item(item_id):
    item = db.session.get(Item, item_id)

    if item is None:
        return redirect(url_for("items"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    found_location = request.form.get("found_location", "").strip()
    found_date = request.form.get("found_date", "").strip()
    photo = request.files.get("photo")

    if not name or not description or not found_location or not found_date:
        return redirect(url_for("items"))

    item.name = name
    item.description = description
    item.found_location = found_location
    item.found_date = found_date

    if photo and photo.filename:
        if not allowed_file(photo.filename):
            return redirect(url_for("items"))
        if not cloudinary_ready():
            return redirect(url_for("items"))
        item.photo_url = upload_photo(photo)

    db.session.commit()

    return redirect(url_for("items", updated="1"))


@app.route("/items/<item_id>/delete", methods=["POST"])
def delete_item(item_id):
    item = db.session.get(Item, item_id)

    if item is not None:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for("items", deleted="1"))


setup_app()


if __name__ == "__main__":
    app.run(debug=True)
