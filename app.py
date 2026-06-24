import os
import json
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import inspect, or_


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
    contact = db.Column(db.String(160), nullable=False, default="")
    photo_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


def setup_app():
    """Create the database table we need."""
    with app.app_context():
        db.create_all()
        ensure_item_columns()


def ensure_item_columns():
    """Add the contact column if an older table does not have it yet."""
    inspector = inspect(db.engine)

    if "item" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("item")}

    if "contact" not in columns:
        with db.engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE item ADD COLUMN contact VARCHAR(160) DEFAULT ''"
            )


def cloudinary_ready():
    """Check if Cloudinary keys exist."""
    return bool(
        os.environ.get("CLOUDINARY_CLOUD_NAME")
        and os.environ.get("CLOUDINARY_API_KEY")
        and os.environ.get("CLOUDINARY_API_SECRET")
    )


def openai_ready():
    """Check if the OpenAI key exists."""
    return bool(os.environ.get("OPENAI_API_KEY"))


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


def normalize_ai_data(data):
    """Clean the structured AI response before using it in the form."""
    return {
        "name": str(data.get("name", "")).strip(),
        "description": str(data.get("description", "")).strip(),
        "found_location": str(data.get("found_location", "")).strip(),
    }


def extract_keywords(text):
    """Pick simple keywords from text."""
    return sorted({word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2})


def analyze_image_with_ai(photo_url):
    """Ask OpenAI to suggest a few fields from the uploaded image."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model_name = os.environ.get("OPENAI_VISION_MODEL", "gpt-4.1")
    prompt = """
Look at this photo of one found item.
Extract simple item details from the image.
Keep the name short.
Keep the description to 1 or 2 simple sentences.
If the image does not show the location, use an empty string for found_location.
""".strip()

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": photo_url},
                    },
                ],
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "found_item_details",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "found_location": {"type": "string"},
                    },
                    "required": ["name", "description", "found_location"],
                    "additionalProperties": False,
                },
            },
        },
        max_tokens=250,
    )

    message = response.choices[0].message

    if getattr(message, "refusal", None):
        raise ValueError("The AI refused to analyze this image.")

    return normalize_ai_data(json.loads(message.content or "{}"))


def fallback_lost_report_data(form_data):
    """Build a simple text-only version when AI is not available."""
    combined_text = " ".join(
        [
            form_data.get("name", ""),
            form_data.get("description", ""),
            form_data.get("lost_location", ""),
        ]
    )

    return {
        "name": form_data.get("name", "").strip(),
        "normalized_description": form_data.get("description", "").strip(),
        "category": "",
        "color": "",
        "keywords": extract_keywords(combined_text)[:6],
    }


def normalize_lost_report_with_ai(form_data):
    """Turn the lost report into cleaner structured data for matching."""
    fallback_data = fallback_lost_report_data(form_data)

    if not openai_ready():
        return fallback_data

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model_name = os.environ.get("OPENAI_MATCH_MODEL", "gpt-4.1")
    prompt = f"""
Read this lost item report and clean it up for matching.

Item name: {form_data.get("name", "")}
Description: {form_data.get("description", "")}
Lost location: {form_data.get("lost_location", "")}
Lost date: {form_data.get("lost_date", "")}

Return structured output for matching.
Keep category and color very short.
Pick up to 6 useful keywords.
""".strip()

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "lost_item_details",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "normalized_description": {"type": "string"},
                            "category": {"type": "string"},
                            "color": {"type": "string"},
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": [
                            "name",
                            "normalized_description",
                            "category",
                            "color",
                            "keywords",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            max_tokens=250,
        )

        message = response.choices[0].message

        if getattr(message, "refusal", None):
            return fallback_data

        data = json.loads(message.content or "{}")
        return {
            "name": str(data.get("name", fallback_data["name"])).strip(),
            "normalized_description": str(
                data.get("normalized_description", fallback_data["normalized_description"])
            ).strip(),
            "category": str(data.get("category", "")).strip(),
            "color": str(data.get("color", "")).strip(),
            "keywords": [
                str(keyword).strip().lower()
                for keyword in data.get("keywords", fallback_data["keywords"])
                if str(keyword).strip()
            ][:6],
        }
    except Exception:
        return fallback_data


def score_match(report_data, item):
    """Give one found item a simple match score."""
    score = 0
    reasons = []
    item_text = " ".join(
        [item.name, item.description, item.found_location, item.contact]
    ).lower()
    report_name = report_data.get("name", "").lower()
    report_description = report_data.get("normalized_description", "").lower()
    report_location = report_data.get("lost_location", "").lower()
    report_keywords = report_data.get("keywords", [])
    report_color = report_data.get("color", "").lower()
    report_category = report_data.get("category", "").lower()

    if report_name and (report_name in item.name.lower() or item.name.lower() in report_name):
        score += 4
        reasons.append("Similar item name")

    if report_location and report_location == item.found_location.lower():
        score += 3
        reasons.append("Same location")

    if report_data.get("lost_date") == item.found_date:
        score += 2
        reasons.append("Same date")

    keyword_hits = 0
    for keyword in report_keywords:
        if keyword in item_text:
            keyword_hits += 1

    if keyword_hits:
        score += min(keyword_hits, 3)
        reasons.append("Matching description words")

    if report_color and report_color in item_text:
        score += 1
        reasons.append("Same color")

    if report_category and report_category in item_text:
        score += 1
        reasons.append("Same category")

    if report_description and report_description in item.description.lower():
        score += 2
        reasons.append("Very similar description")

    return score, reasons


def score_label(score):
    """Turn the score into an easy label for students."""
    if score >= 8:
        return "Strong match"
    if score >= 5:
        return "Possible match"
    return "Weak match"


def find_suggested_matches(report_data):
    """Compare the lost report with all found items."""
    matches = []
    all_items = Item.query.order_by(Item.created_at.desc()).all()

    for item in all_items:
        score, reasons = score_match(report_data, item)

        if score > 0:
            matches.append(
                {
                    "item": item,
                    "score": score,
                    "label": score_label(score),
                    "reasons": reasons[:3],
                }
            )

    matches.sort(key=lambda match: match["score"], reverse=True)
    return matches[:5]


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
                Item.contact.ilike(like_text),
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
        ai_ready=openai_ready(),
    )


@app.route("/lost-report")
def lost_report():
    return render_template(
        "lost_report.html",
        error=None,
        form_data={},
        ai_ready=openai_ready(),
    )


@app.route("/autofill", methods=["POST"])
def autofill_item():
    """Read an uploaded image with AI and return suggested values."""
    photo = request.files.get("photo")

    if not photo or not photo.filename:
        return jsonify({"error": "Please choose an image first."}), 400

    if not allowed_file(photo.filename):
        return jsonify({"error": "Please upload a valid image."}), 400

    if not cloudinary_ready():
        return jsonify({"error": "Please add Cloudinary keys first."}), 400

    if not openai_ready():
        return jsonify({"error": "Please add OPENAI_API_KEY first."}), 400

    try:
        photo_url = upload_photo(photo)
        ai_data = analyze_image_with_ai(photo_url)
    except Exception:
        return jsonify({"error": "AI could not read this image right now."}), 500

    return jsonify(
        {
            "message": "AI filled some fields. You can still change them.",
            "photo_url": photo_url,
            "name": ai_data["name"],
            "description": ai_data["description"],
            "found_location": ai_data["found_location"],
        }
    )


@app.route("/lost-report/matches", methods=["POST"])
def lost_report_matches():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    lost_location = request.form.get("lost_location", "").strip()
    lost_date = request.form.get("lost_date", "").strip()
    contact = request.form.get("contact", "").strip()
    form_data = {
        "name": name,
        "description": description,
        "lost_location": lost_location,
        "lost_date": lost_date,
        "contact": contact,
    }

    if not name or not description or not lost_location or not lost_date or not contact:
        return (
            render_template(
                "lost_report.html",
                error="Please fill every field before searching for matches.",
                form_data=form_data,
                ai_ready=openai_ready(),
            ),
            400,
        )

    ai_report = normalize_lost_report_with_ai(form_data)
    report_data = {
        **form_data,
        **ai_report,
    }
    matches = find_suggested_matches(report_data)

    return render_template(
        "match_results.html",
        report=form_data,
        ai_report=ai_report,
        matches=matches,
        ai_ready=openai_ready(),
    )


@app.route("/submit", methods=["POST"])
def submit_item():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    found_location = request.form.get("found_location", "").strip()
    found_date = request.form.get("found_date", "").strip()
    contact = request.form.get("contact", "").strip()
    saved_photo_url = request.form.get("photo_url", "").strip()
    photo = request.files.get("photo")
    form_data = {
        "name": name,
        "description": description,
        "found_location": found_location,
        "found_date": found_date,
        "contact": contact,
        "photo_url": saved_photo_url,
    }

    # Simple validation for beginners.
    if (
        not name
        or not description
        or not found_location
        or not found_date
        or not contact
        or (not saved_photo_url and not photo)
    ):
        return (
            render_template(
                "index.html",
                error="Please fill every field and add a photo.",
                form_data=form_data,
                using_cloudinary=cloudinary_ready(),
                ai_ready=openai_ready(),
            ),
            400,
        )

    if saved_photo_url:
        photo_url = saved_photo_url
    else:
        if not photo.filename or not allowed_file(photo.filename):
            return (
                render_template(
                    "index.html",
                    error="Please upload a valid image.",
                    form_data=form_data,
                    using_cloudinary=cloudinary_ready(),
                    ai_ready=openai_ready(),
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
                    ai_ready=openai_ready(),
                ),
                400,
            )

        photo_url = upload_photo(photo)

    item = Item(
        name=name,
        description=description,
        found_location=found_location,
        found_date=found_date,
        contact=contact,
        photo_url=photo_url,
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
    contact = request.form.get("contact", "").strip()
    photo = request.files.get("photo")

    if not name or not description or not found_location or not found_date or not contact:
        return redirect(url_for("items"))

    item.name = name
    item.description = description
    item.found_location = found_location
    item.found_date = found_date
    item.contact = contact

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
