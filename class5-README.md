# Lost & Found Flask App - Class 5

This is the Class 5 version of the Flask lost-and-found project.

This version keeps the normal Flask database app, but adds AI features too.

Main new ideas:

- AI autofill from an uploaded image
- AI-based lost-item matching
- contact field for phone or email
- OpenAI API key in `.env`
- PostgreSQL database
- Cloudinary image storage

This file does not replace the Class 4 README.

## What is new in Class 5?

In this version, a student can:

- upload a photo of a found item
- click `Auto Fill With AI`
- let AI suggest the item name
- let AI suggest the item description
- edit the AI text before saving
- add contact details
- save the item in PostgreSQL
- report a lost item on a separate page
- let AI clean the lost-item report
- see possible found-item matches

## Main pages

The app now has 3 main pages.

### Page 1: Add found item

Route:

```text
/
```

This page is used to:

- upload a found-item photo
- use AI autofill
- enter item details
- save the final item

### Page 2: View found items

Route:

```text
/items
```

This page is used to:

- see saved items
- search items
- filter items
- edit items
- delete items

### Page 3: Report lost item

Route:

```text
/lost-report
```

This page is used to:

- report a lost item
- enter lost date and location
- enter contact details
- let AI clean the report
- see possible matches from found items

## Big concepts

### What is AI in this project?

AI means the app can use a smart model to understand text or images.

In this project, AI is not controlling everything.

It is only helping in 2 places:

1. reading a found-item image
2. cleaning a lost-item report for matching

So AI is a helper, not the main app.

### What is an AI API?

API means Application Programming Interface.

It is a way for one program to talk to another service.

In this project:

- our Flask app is one program
- OpenAI is another service on the internet

The Flask app sends a request to OpenAI.

OpenAI sends a response back.

So we are using OpenAI through its API.

### What is OpenAI?

OpenAI is a company that provides AI models through an API.

These models can:

- understand text
- understand images
- generate text
- follow instructions
- return structured data

In our project, OpenAI is used in 2 different ways:

- image understanding
- text cleanup for matching

### What exactly are we using OpenAI for?

#### 1. AI autofill for found items

When a user uploads a photo on the found-item page:

1. Flask uploads the image to Cloudinary
2. Cloudinary gives back an image URL
3. Flask sends that image URL to OpenAI
4. OpenAI looks at the image
5. OpenAI returns:
   - item name
   - short description
   - possible location if visible
6. Flask sends that data back to the page
7. JavaScript fills the form

The student can still change the text before saving.

#### 2. AI cleanup for lost-item matching

When a user fills the lost-item report:

1. Flask reads the lost item text
2. Flask sends that text to OpenAI
3. OpenAI cleans the report into simpler structured details
4. Flask uses those cleaned details to compare with saved found items
5. Flask shows the best matches

Here OpenAI helps with understanding the lost report better.

### What is structured output?

Structured output means the AI returns data in a fixed shape.

Example:

```json
{
  "name": "Black water bottle",
  "description": "Black bottle with a sticker",
  "found_location": "Library table"
}
```

This is better than getting a random paragraph, because code can read this more easily.

In this project, we use structured output so OpenAI gives predictable fields.

That makes the app safer and easier to code.

### What is an external API?

An external API is a tool outside our own project.

Examples in this app:

- Cloudinary
- OpenAI

Our code runs inside Flask, but some special work is done by outside services:

- Cloudinary stores images
- OpenAI understands images and text

### Why do we use Cloudinary before OpenAI?

The browser first sends the image to Flask.

Then Flask uploads the image to Cloudinary.

Cloudinary returns an image URL.

Then Flask sends that image URL to OpenAI.

This helps because OpenAI can read the hosted image from the URL.

So the image flow is:

1. student chooses image
2. browser sends image to Flask
3. Flask uploads image to Cloudinary
4. Cloudinary returns image URL
5. Flask sends image URL to OpenAI
6. OpenAI returns suggestions

### What is a contact field?

The contact field stores how someone can reach the student.

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

## Database idea

The database stores found items.

Right now it stores:

- item name
- description
- found location
- found date
- contact
- photo URL
- time created

The lost-item page does not save a separate lost-report table yet.

In version 1, the lost report is used only to find matches.

## Environment variables

Environment variables are values stored outside the code.

They help us keep:

- secret keys
- database links
- settings

This app uses:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/lostfound
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-api-key
OPENAI_VISION_MODEL=gpt-4.1
OPENAI_MATCH_MODEL=gpt-4.1
```

### What each variable means

- `DATABASE_URL`: tells Flask where the PostgreSQL database is
- `CLOUDINARY_CLOUD_NAME`: your Cloudinary account name
- `CLOUDINARY_API_KEY`: Cloudinary API key
- `CLOUDINARY_API_SECRET`: Cloudinary secret key
- `OPENAI_API_KEY`: your OpenAI secret key
- `OPENAI_VISION_MODEL`: the OpenAI model used for image autofill
- `OPENAI_MATCH_MODEL`: the OpenAI model used for lost-item text cleanup

### Why is `.env` important?

`.env` keeps important values outside the Python code.

This is safer because:

- secrets are not hard-coded in `app.py`
- different computers can use different keys
- production and local machine can use different values

### Why is `.gitignore` important?

`.gitignore` stops `.env` from being committed to Git.

That is important because API keys and passwords must stay private.

## How to get an OpenAI API key

These steps may change a little in the future, but the basic idea is:

1. Go to the OpenAI platform website.
2. Create an account or sign in.
3. Open the API keys section in your dashboard.
4. Create a new secret key.
5. Copy the key.
6. Paste it into `.env` like this:

```env
OPENAI_API_KEY=your-openai-api-key
```

Important:

- do not share this key with others
- do not put it in frontend JavaScript
- do not upload it to GitHub
- keep it only in `.env`

## How to get the other keys

### PostgreSQL

You need a PostgreSQL database URL.

That usually looks like:

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

You can get this from:

- your local PostgreSQL setup
- Neon
- Supabase
- Render
- another PostgreSQL provider

### Cloudinary

You need:

- cloud name
- API key
- API secret

These come from your Cloudinary dashboard.

Paste them in `.env`.

## How we are using OpenAI exactly

This is the most important AI part of the project.

### Found-item image autofill

In `app.py`, the function `analyze_image_with_ai()` sends the image URL to OpenAI.

OpenAI is asked to return structured fields like:

- `name`
- `description`
- `found_location`

The code then reads that response and fills the form.

Simple idea:

```python
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": photo_url}},
            ],
        }
    ],
    response_format={...},
)
```

So:

- text tells the AI what to do
- image URL gives the photo
- `response_format` forces structured output

### Lost-item AI matching

In `app.py`, the function `normalize_lost_report_with_ai()` sends the lost report text to OpenAI.

OpenAI returns cleaned fields like:

- `name`
- `normalized_description`
- `category`
- `color`
- `keywords`

Then the app uses plain Python scoring to compare the lost report with found items.

That means OpenAI is helping to prepare the data, but the final matching is still controlled by our Flask code.

This is good because:

- code stays easy to understand
- app still works even if AI fails
- matching logic is readable for students

## Why we are not letting AI do everything

If AI did the whole matching by itself, the app would be harder to understand and harder to test.

So we use a mixed method:

- AI for understanding
- Python for scoring and decision-making

This is a good beginner-friendly design.

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

### Example found-item form idea

This is the kind of HTML used on the add found-item page:

```html
<input type="file" name="photo" accept="image/*" />
<button type="button">Auto Fill With AI</button>
<input type="text" name="name" />
<textarea name="description"></textarea>
<input type="text" name="contact" />
```

### Example AI autofill route

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

What this route does:

1. gets the uploaded image
2. uploads it to Cloudinary
3. sends the image URL to OpenAI
4. gets structured AI fields back
5. returns them to the browser as JSON

### Example OpenAI client setup

```python
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
```

### Example image AI helper

This helper is the main AI logic for found-item autofill:

```python
def analyze_image_with_ai(photo_url):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_VISION_MODEL", "gpt-4.1"),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this found item."},
                    {"type": "image_url", "image_url": {"url": photo_url}},
                ],
            }
        ],
        response_format={...},
    )

    return json.loads(response.choices[0].message.content)
```

What this helper does:

- creates the OpenAI client
- sends both text and image URL
- asks for structured output
- returns fields the form can use

### Example lost-item page idea

This is the kind of HTML used on the lost-item page:

```html
<form action="/lost-report/matches" method="post">
  <input type="text" name="name" />
  <textarea name="description"></textarea>
  <input type="text" name="lost_location" />
  <input type="date" name="lost_date" />
  <input type="text" name="contact" />
  <button type="submit">Find Possible Matches</button>
</form>
```

### Example lost-item match route

```python
@app.route("/lost-report/matches", methods=["POST"])
def lost_report_matches():
    form_data = {
        "name": request.form.get("name", "").strip(),
        "description": request.form.get("description", "").strip(),
        "lost_location": request.form.get("lost_location", "").strip(),
        "lost_date": request.form.get("lost_date", "").strip(),
        "contact": request.form.get("contact", "").strip(),
    }

    ai_report = normalize_lost_report_with_ai(form_data)
    report_data = {**form_data, **ai_report}
    matches = find_suggested_matches(report_data)

    return render_template(
        "match_results.html",
        report=form_data,
        ai_report=ai_report,
        matches=matches,
    )
```

What this route does:

1. reads the lost-item form
2. sends the report to the AI cleanup helper
3. mixes the cleaned AI data with the form data
4. finds the best matching found items
5. opens the results page

### Example lost-item AI cleanup helper

This helper cleans the lost report before matching:

```python
def normalize_lost_report_with_ai(form_data):
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MATCH_MODEL", "gpt-4.1"),
        messages=[{"role": "user", "content": prompt}],
        response_format={...},
    )

    data = json.loads(response.choices[0].message.content)
    return {
        "name": data["name"],
        "normalized_description": data["normalized_description"],
        "category": data["category"],
        "color": data["color"],
        "keywords": data["keywords"],
    }
```

What this helper does:

- sends the lost report text to OpenAI
- asks OpenAI to clean it into a fixed structure
- returns easy fields for Python matching

### Example match scoring helper

This helper compares one lost report with one found item:

```python
def score_match(report_data, item):
    score = 0

    if report_data["name"].lower() in item.name.lower():
        score += 4

    if report_data["lost_location"].lower() == item.found_location.lower():
        score += 3

    if report_data["lost_date"] == item.found_date:
        score += 2

    for keyword in report_data["keywords"]:
        if keyword in item.description.lower():
            score += 1

    return score
```

What this helper does:

- checks similar names
- checks same place
- checks same date
- checks shared keywords
- gives a score

Then the app sorts the scores and shows the strongest matches first.

### Example match result page idea

```html
<section>
  <h3>Lost Item Summary</h3>
  <p>Name: Black water bottle</p>
</section>

<section>
  <h3>AI Clean Match Data</h3>
  <p>Category: bottle</p>
  <p>Color: black</p>
</section>

<section>
  <article>
    <h3>Black bottle</h3>
    <p>Strong match</p>
    <p>Found at: Library</p>
  </article>
</section>
```

### How the new pages work

#### `/lost-report`

This page is the input page for lost items.

Student writes:

- what was lost
- where it was lost
- when it was lost
- how to contact them

Then the student clicks:

```text
Find Possible Matches
```

#### `/lost-report/matches`

This is the results step.

Flask does not just show the raw lost report.

It does 3 things:

1. reads the report
2. asks OpenAI to clean it
3. compares it with found items

Then it shows:

- original report
- AI cleaned data
- best matches
- match reasons
- found-item contact

#### `match_results.html`

This page is important because it teaches students that AI does not work alone.

The page shows both:

- what the user wrote
- what AI understood

This helps students compare:

- original input
- cleaned AI output
- final matching result

## Backend flow

### Normal found-item save

If the student fills the form normally:

1. Flask reads the form
2. Flask uploads the photo to Cloudinary
3. Flask saves the item in PostgreSQL
4. Flask opens the items page

### AI autofill save

If the student uses AI autofill:

1. student chooses image
2. student clicks `Auto Fill With AI`
3. Flask uploads image to Cloudinary
4. Flask sends the image URL to OpenAI
5. OpenAI sends structured text suggestions
6. JavaScript fills the form
7. student checks and edits the text
8. student clicks save
9. Flask saves the final data to PostgreSQL

### Lost-item matching

If the student reports a lost item:

1. student opens `/lost-report`
2. student fills the lost-item form
3. Flask reads the text
4. OpenAI cleans the report into structured details
5. Flask compares the report with found items
6. Flask gives each possible match a score
7. Flask shows the result page

### Lost-item matching in very simple words

The lost-item matching feature works like this:

1. user writes a lost item report
2. AI cleans the report into simpler fields
3. Python compares those fields with found items
4. each found item gets a score
5. strongest scores are shown first

So the real matching is a team effort:

- OpenAI helps understand the text
- Python does the final scoring

### Why this is a good design for students

This design is easier to learn because:

- AI is used only where it is helpful
- matching rules are visible in Python
- results are easier to test
- the app still makes sense even without advanced AI knowledge

## Files used in Class 5

### `app.py`

Main Flask backend file.

It contains:

- model
- routes
- Cloudinary upload logic
- OpenAI image reading logic
- OpenAI lost-item matching logic
- database save logic

### `templates/index.html`

Add found-item page.

It contains:

- form
- image upload
- AI autofill button
- small JavaScript for autofill

### `templates/items.html`

Found-items page.

It contains:

- item cards
- search
- filter
- edit popup
- delete button

### `templates/lost_report.html`

Lost-item page.

It contains:

- lost item form
- contact field
- AI helper details

### `templates/match_results.html`

Lost-item result page.

It contains:

- lost report summary
- AI cleaned summary
- suggested found-item matches

### `tests/test_app.py`

This file checks if the app still works.

It tests things like:

- saving an item
- AI autofill route
- lost report page
- lost item matches
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
