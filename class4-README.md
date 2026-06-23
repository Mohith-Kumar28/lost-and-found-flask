# Lost & Found Flask App

This is a simple school project made with Flask.

It helps us learn how a website can:

- take data from a form
- save data in a database
- show saved data on another page
- upload images
- edit and delete items
- search and filter items

This README is written in a simple way for a Class 4 student.

## What this app does

In this app, a student can:

- add a found item
- write the item name
- write a small description
- say where the item was found
- choose the date
- upload a photo
- see all items
- search items
- filter items
- edit an item
- delete an item

## Big idea

This project has 2 main parts:

- frontend
- backend

### Frontend

Frontend means the part we can see on the screen.

In this project, frontend includes:

- the form
- the buttons
- the cards
- the edit popup
- the search box
- the filter box
- the page design

### Backend

Backend means the part working behind the scenes.

In this project, backend:

- receives form data
- checks the data
- saves the data in the database
- uploads the image
- loads items from the database
- updates items
- deletes items
- filters items

## Important concepts

This section explains the big ideas used in the project.

### What is a database?

A database is a place where an app stores information in an organized way.

You can think of it like a smart notebook.

Instead of writing everything randomly, the data is saved in a proper structure.

In this project, the database stores:

- item name
- description
- found location
- found date
- photo link
- time the item was created

Why a database is useful:

- data stays saved
- data is easy to search
- data is easier to update
- data is easier to delete
- bigger apps need this kind of storage

### What is PostgreSQL?

PostgreSQL is a real database system.

It is often called Postgres for short.

It is stronger and more professional than saving data in a text file.

In this project, PostgreSQL stores the lost-and-found item details.

### PostgreSQL fundamentals

Here are some important PostgreSQL ideas:

- database: the full container that stores data
- table: one organized set of data
- row: one single item in the table
- column: one field in that row

Example:

- table name: `item`
- one row: one lost item
- columns: `name`, `description`, `found_location`, `found_date`

Think of it like a school attendance sheet:

- the whole register book is like the database
- one page is like a table
- one student line is like a row
- each box on the line is like a column

### What is SQL?

SQL is the language used to talk to databases.

It helps us:

- save data
- read data
- update data
- delete data

These are often called:

- create
- read
- update
- delete

Together, people call this CRUD.

### What is Flask-SQLAlchemy?

Flask-SQLAlchemy helps Python talk to the database in an easier way.

Instead of writing lots of raw SQL by hand, we can write Python code like this:

```python
item = Item(name="Blue bottle", description="Found near the lab")
db.session.add(item)
db.session.commit()
```

So:

- PostgreSQL is the real database
- SQL is the language for databases
- Flask-SQLAlchemy is the helper library that lets Flask use the database more easily

### What is a model?

A model is the Python class that describes how one kind of data should look.

In this app, the `Item` model says:

- every item has a name
- every item has a description
- every item has a location
- every item has a date
- every item has a photo URL

So the model is like a blueprint.

### What is a route?

A route is the path in the website that Flask listens to.

Examples:

- `/` shows the add item page
- `/items` shows the saved items page
- `/submit` receives the form data

You can think of a route like a classroom door label.

Each label tells you which room to enter.

### What is a template?

A template is an HTML page Flask can fill with real data.

For example, Flask can send a list of items into `items.html`, and then the template shows them on the page.

So templates help connect:

- Python code
- HTML page
- real saved data

### What is a form?

A form is the part of the web page where the user types or selects information.

In this app, the form is used to send:

- text
- date
- image file

from the browser to Flask.

### What is a query?

A query is a request for data.

When the app searches or filters items, it makes a query to the database.

Examples:

- give me all items
- give me items from the library
- give me items with the word "bottle"

### What is a CDN?

CDN means Content Delivery Network.

A CDN is a system that helps deliver files, especially images, faster and more easily.

In this project, Cloudinary is used like an image CDN.

That means:

- the app uploads the image to Cloudinary
- Cloudinary stores the image
- Cloudinary gives back a link
- the app saves that link in the database
- the browser shows the image from that link

Why a CDN is useful:

- images do not need to stay inside the Flask project folder
- image delivery is faster and easier
- it is better for real websites

### What is Cloudinary?

Cloudinary is an image service on the internet.

It helps us:

- upload images
- store images
- get image URLs
- show those images on the website

In simple words, Cloudinary is a special tool for handling images.

### What is an external API?

An external API is a service outside our app that we talk to through code.

Cloudinary is an external API in this project.

That means:

- our Flask app sends the image to Cloudinary
- Cloudinary responds with information
- our app uses that response

So the app is not working alone.

It is using help from another online service.

### What are environment variables?

Environment variables are values stored outside the code.

They are used for important settings like:

- database URL
- Cloudinary keys
- secret values

This is useful because:

- we do not hard-code secret values in the app
- we can change settings without editing the code
- production and local setup can use different values

### What is the `.env` file?

The `.env` file is a simple file that stores environment variables.

In this project, `.env` stores:

- `DATABASE_URL`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

So the `.env` file is like the settings page for the project.

### Why should secrets stay out of the code?

Things like database passwords and API keys should not be written directly in Python files.

If they are written in code:

- they may get shared by mistake
- they may get uploaded to GitHub
- other people may misuse them

That is why `.env` and `.gitignore` are important.

### What happens when an image is uploaded?

Here is the story in simple order:

1. The user chooses an image in the form.
2. The browser sends that image to Flask.
3. Flask checks if the file looks like an image.
4. Flask sends that file to Cloudinary.
5. Cloudinary returns an image URL.
6. Flask saves that URL in PostgreSQL.
7. The items page later uses that URL to show the image.

### What happens when search works?

Here is the simple idea:

1. The user types search text.
2. The browser sends that search text in the URL.
3. Flask reads the value from `request.args`.
4. Flask makes a database query.
5. The database sends back matching rows.
6. Flask shows only those matching items.

### What is the difference between local code and external services?

Local code means the code and files inside this project.

Examples:

- `app.py`
- HTML templates
- CSS
- tests

External services mean tools outside this project.

Examples:

- PostgreSQL database server
- Cloudinary image service

So this app is a mix of:

- code written by us
- services used from outside

## What changed in this new version

Before, the app used a local JSON file.

Now, the app is updated to use a real database.

The new version now has:

- a database using Flask-SQLAlchemy
- PostgreSQL support with `DATABASE_URL`
- Cloudinary support for image storage
- edit route
- delete route
- edit modal on the items page
- search option
- filter by place
- filter by date

## How the app works

### 1. Open the form page

The browser opens:

```text
/
```

This shows the page where we can fill the form.

### 2. Fill the form

The student writes:

- item name
- description
- place found
- date found
- photo

### 3. Submit the form

When the student clicks the button:

- Flask receives the form data
- Flask checks the fields
- Flask checks the image type
- the image is uploaded
- the item is saved in the database

### 4. View saved items

After saving, the app opens:

```text
/items
```

This page shows all saved items.

### 5. Search and filter

On the items page, the user can:

- search by item name
- search by description
- search by place
- filter by place
- filter by date

### 6. Edit and delete

Each item card has:

- an Edit button
- a Delete button

The Edit button opens a modal.

A modal is a small popup box on the page.

The Delete button removes the item.

## Database in very simple words

A database is a place to store information neatly.

You can think of it like a smart notebook for the app.

In this project:

- each saved item becomes one row in the database
- the app can read the rows later
- the app can change or delete rows later

Example model code:

```python
class Item(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    found_location = db.Column(db.String(120), nullable=False)
    found_date = db.Column(db.String(10), nullable=False)
    photo_url = db.Column(db.Text, nullable=False)
```

## Which database does this app use?

This app uses PostgreSQL from the `.env` file.

### PostgreSQL

This is the main real database choice.

The app reads `DATABASE_URL` from `.env`.

Example:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/lostfound"
```

If `DATABASE_URL` is missing, the app shows an error and stops.

## Images in very simple words

This app stores images in Cloudinary.

### Cloudinary

Cloudinary is an image service on the internet.

If these 3 values are added, the app can upload images to Cloudinary:

- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

Example:

```bash
export CLOUDINARY_CLOUD_NAME="your-cloud-name"
export CLOUDINARY_API_KEY="your-api-key"
export CLOUDINARY_API_SECRET="your-api-secret"
```

If Cloudinary keys are not added, the app cannot save images.

## Environment file

This project now uses:

- `.env.example`
- `.env`

### `.env.example`

This is the sample file.

It shows which keys are needed.

### `.env`

This is your real local file.

Put your real PostgreSQL and Cloudinary values here.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/lostfound
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Why `.env` is in `.gitignore`

`.env` should not be committed because it can contain secret keys.

## Code examples

These small examples show the kind of code used in the project.

### Example route

This route shows the home page:

```python
@app.route("/")
def index():
    return render_template(
        "index.html",
        error=None,
        form_data={},
        using_cloudinary=cloudinary_ready(),
    )
```

### Example save route

This route receives the form data and saves an item:

```python
@app.route("/submit", methods=["POST"])
def submit_item():
    name = request.form.get("name", "").strip()
    photo = request.files.get("photo")

    item = Item(
        name=name,
        description=request.form.get("description", "").strip(),
        found_location=request.form.get("found_location", "").strip(),
        found_date=request.form.get("found_date", "").strip(),
        photo_url=upload_photo(photo),
    )

    db.session.add(item)
    db.session.commit()
    return redirect(url_for("items", added="1"))
```

### Example search code

This code filters the items list:

```python
search = request.args.get("search", "").strip()

if search:
    like_text = f"%{search}%"
    items_query = items_query.filter(
        or_(
            Item.name.ilike(like_text),
            Item.description.ilike(like_text),
            Item.found_location.ilike(like_text),
        )
    )
```

### Example HTML form

This is the kind of HTML used in the form page:

```html
<form
  action="{{ url_for('submit_item') }}"
  method="post"
  enctype="multipart/form-data"
>
  <input type="text" name="name" required />
  <textarea name="description" required></textarea>
  <input type="date" name="found_date" required />
  <input type="file" name="photo" accept="image/*" required />
  <button type="submit">Save item</button>
</form>
```

## Important files

```text
flask/
├── app.py
├── main.py
├── static/
│   ├── style.css
├── templates/
│   ├── base.html
│   └── index.html
├── tests/
│   └── test_app.py
├── pyproject.toml
└── README.md
```

## File jobs

### `app.py`

This is the main Python file.

It:

- starts Flask
- connects to the database
- creates routes
- saves items
- edits items
- deletes items
- searches items
- filters items
- uploads images

### `templates/index.html`

This is the form page.

It is used to add a new item.

### `templates/items.html`

This is the items page.

It is used to:

- show saved items
- search items
- filter items
- edit items
- delete items

### `templates/base.html`

This is the shared layout file.

It keeps common page parts like:

- title
- header
- navigation

### `static/style.css`

This file makes the app look nice.

It styles:

- the form
- the cards
- the buttons
- the modal
- the search area

### `tests/test_app.py`

This file checks that the app works properly.

It tests things like:

- home page loads
- item saves
- search works
- filters work
- edit works
- delete works

### `pyproject.toml`

This file lists the packages the project needs.

Important packages now include:

- `flask`
- `flask-sqlalchemy`
- `psycopg`
- `cloudinary`

## How to run the project

### 1. Open the project folder

Open the terminal in the project folder.

### 2. Install the packages

```bash
uv sync
```

### 3. Start the app

```bash
uv run python app.py
```

### 4. Open the website

Open this link:

```text
http://127.0.0.1:5000
```

## Useful routes

- `/` = main page
- `/items` = items page
- `/submit` = save item route
- `/items/<item_id>/edit` = edit item route
- `/items/<item_id>/delete` = delete item route

## How to run the tests

```bash
uv run python -m unittest discover -s tests
```

## Easy summary

This project teaches:

- forms
- routes
- templates
- CSS
- database basics
- image upload basics
- search
- filters
- edit
- delete

## Final note

This version is still kept simple on purpose.

The code uses:

- short functions
- easy route names
- simple comments
- beginner-friendly structure

That makes it easier for young students to read and learn.
