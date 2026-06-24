# Lost & Found Flask App - Class 5

This is the Class 5 version of the Flask lost-and-found project.

This version adds a few new ideas:

- AI autofill from an uploaded image
- contact field for phone or email
- OpenAI API key in `.env`
- the same database + Cloudinary setup from Class 4

This file does not replace the Class 4 README.

## What is new in Class 5?

In this version, a student can:

- upload an image
- click `Auto Fill With AI`
- let AI suggest the item name
- let AI suggest a short description
- edit the AI text if needed
- add contact details like phone or email
- save the item to the database
- view, search, edit, and delete items later

## App flow

The app still has 2 main pages.

### Page 1: Add item

Route:

```text
/
```

This page is used to:

- choose a photo
- ask AI to read the photo
- fill the form
- save the final item

### Page 2: View items

Route:

```text
/items
```

This page is used to:

- see all items
- search items
- filter items
- edit items
- delete items

## New concepts

### What is AI autofill?

AI autofill means the app looks at the uploaded image and tries to suggest text.

In this project, the AI tries to suggest:

- item name
- short description
- sometimes a possible location if the image shows one

The user can still change the text before saving.

So the AI is helping, not taking full control.

### What is OpenAI?

OpenAI is an external API service.

Our Flask app sends the image to OpenAI and asks:

```text
What item is in this picture? Give a short name and description.
```

Then OpenAI sends back a response.

The app reads that response and fills the form.

### What is an external API?

An external API is a tool outside our own project.

Examples in this project:

- Cloudinary
- OpenAI

Our app code lives in the Flask project.

But some work is done by outside services:

- Cloudinary stores the image
- OpenAI understands the image

### Why do we use Cloudinary first?

The image starts in the browser.

The app uploads it to Cloudinary first.

Cloudinary gives a photo URL.

Then OpenAI can read that photo using the URL.

So the flow is:

1. user uploads image
2. Flask sends image to Cloudinary
3. Cloudinary returns image URL
4. Flask sends image URL to OpenAI
5. OpenAI returns text suggestions
6. Flask fills the form

### What is a contact field?

The contact field stores how someone can reach the student who submitted the item.

It can store:

- phone number
- email address

Example:

```text
9876543210
```

or

```text
student@example.com
```

### What is still stored in the database?

The database now stores:

- item name
- description
- found location
- found date
- contact
- photo URL
- time created

## Environment variables

Environment variables are values stored outside the code.

They help us keep secret values and settings in one place.

This app uses:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/lostfound
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-api-key
```

### Why is `.env` important?

`.env` keeps important values outside the Python code.

This is safer because:

- secrets are not hard-coded
- different people can use different keys
- the same code can work in different places

### Why is `.gitignore` important?

`.gitignore` stops `.env` from being committed to Git.

That is important because API keys and database passwords should stay private.

## Code examples

### Example model

```python
class Item(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    found_location = db.Column(db.String(120), nullable=False, index=True)
    found_date = db.Column(db.String(10), nullable=False, index=True)
    contact = db.Column(db.String(160), nullable=False, default="")
    photo_url = db.Column(db.Text, nullable=False)
```

### Example AI route

```python
@app.route("/autofill", methods=["POST"])
def autofill_item():
    photo = request.files.get("photo")
    photo_url = upload_photo(photo)
    ai_data = analyze_image_with_ai(photo_url)

    return jsonify(
        {
            "name": ai_data["name"],
            "description": ai_data["description"],
            "found_location": ai_data["found_location"],
            "photo_url": photo_url,
        }
    )
```

### Example OpenAI call

```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this found item."},
                {"type": "image_url", "image_url": {"url": photo_url}},
            ],
        }
    ],
)
```

### Example HTML idea

```html
<input type="file" name="photo" accept="image/*" />
<button type="button">Auto Fill With AI</button>
<input type="text" name="name" />
<textarea name="description"></textarea>
<input type="text" name="contact" />
```

## Simple explanation of the backend flow

### Normal save

If the student fills the form normally:

1. Flask reads the form
2. Flask uploads the photo to Cloudinary
3. Flask saves the item in PostgreSQL
4. Flask shows the items page

### AI autofill save

If the student uses AI autofill:

1. student chooses image
2. student clicks `Auto Fill With AI`
3. Flask uploads image to Cloudinary
4. Flask sends the image URL to OpenAI
5. OpenAI sends text suggestions
6. JavaScript fills the form
7. student checks the text
8. student clicks save
9. Flask saves the final data to PostgreSQL

## Files used in Class 5

### `app.py`

Main Flask backend file.

It contains:

- model
- routes
- Cloudinary upload logic
- OpenAI image reading logic
- database save logic

### `templates/index.html`

Add item page.

It contains:

- form
- image upload
- AI autofill button
- small JavaScript for autofill

### `templates/items.html`

Items page.

It contains:

- item cards
- search
- filter
- edit popup
- delete button

### `tests/test_app.py`

This file checks if the app still works.

It tests things like:

- saving an item
- AI autofill route
- editing
- deleting

## How to run

Install packages:

```bash
uv sync
```

Run the app:

```bash
uv run python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Important note

AI is helpful, but it is not perfect.

Sometimes it may:

- guess wrong
- miss details
- give a short description that needs editing

That is why the student should always check the AI-filled text before saving.
