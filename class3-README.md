# Lost & Found Flask App

This is a simple Flask web app for a classroom project.

Students can:

- submit a found item with a name, description, photo, location, and date
- save that data locally in a JSON file
- view all saved items on a separate page

## Start here first

If a student opens this README for the first time, this is the part to read first.

To run this project, we need:

- Python 3
- `uv`

`uv` is a tool that helps us:

- create a Python project
- install packages like Flask
- make a virtual environment
- run Python commands in the project

## Install `uv`

### On macOS with Homebrew

```bash
brew install uv
```

### Or use the official installer

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Official docs:

- [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

## How to create this project from the beginning

This section explains how the project was created from zero.

### 1. Make the folder

```bash
mkdir ~/Desktop/lost-and-found
cd ~/Desktop/lost-and-found
```

This makes a new folder on the desktop and moves into it.

### 2. Create a Python project using `uv`

```bash
uv init --app --name lost-and-found .
```

What this command does:

- `uv init` creates a new Python project
- `--app` says we are making an app, not just a simple script
- `--name lost-and-found` gives the project a name
- `.` means create the project in the current folder

After this step, `uv` creates some starter files for us.

### 3. Add Flask

For this project, Flask was added in `pyproject.toml`.

The important part looks like this:

```toml
dependencies = [
    "flask>=3.1.2",
]
```

What this means:

- `dependencies` means packages this project needs
- `flask` is the web framework we are using
- `>=3.1.2` means version `3.1.2` or newer is okay

Another easy way students can remember this:

- `pyproject.toml` lists what the project needs
- `uv sync` actually installs those things

### 4. Install the packages

```bash
uv sync
```

What this command does:

- creates a virtual environment called `.venv`
- installs Flask and other needed packages
- makes the project ready to run

You can think of `.venv` like a private Python box for this project only.

### 5. Run the app

```bash
uv run python app.py
```

What this command does:

- `uv run` runs the command using this project's environment
- `python app.py` starts our Flask app
  `

### 6. Open the website

Open this link in the browser:

```text
http://127.0.0.1:5000
```

## Quick run steps

If the project is already created and you just want to run it:

1. Open the project folder in VS Code.
2. Open the terminal in that folder.
3. Install packages:

```bash
uv sync
```

4. Start the app:

```bash
uv run python app.py
```

5. Open:

```text
http://127.0.0.1:5000
```

## How to add more packages later

If later you want to add another library, you can use:

```bash
uv add package-name
```

For example:

```bash
uv add flask
```

This is useful later when adding AI libraries or database libraries.

## What this project teaches

This small app teaches some very important web development ideas:

- how a browser shows a web page
- how a form sends data to a server
- how Python can receive that data
- how uploaded images can be saved
- how data can be stored before learning databases
- how one app can have more than one page

## Project structure

```text
lost-and-found/
├── app.py
├── main.py
├── data/
│   └── items.json
├── static/
│   ├── style.css
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── items.html
└── pyproject.toml
```

## Project structure explained slowly

Think of the project like a school team. Each file has a job. No file is there by accident.

### `app.py`

This is the most important file in the project.

It is the main Python file that:

- starts Flask
- creates the routes
- receives form data
- checks if the form is filled properly
- saves photos
- saves item details into the JSON file
- loads saved items and shows them on the listings page

If the whole project were a body, `app.py` would be the brain.

### `main.py`

This is a small helper file that can also start the app.

Students do not need to focus too much on this file right now.
The main learning file is still `app.py`.

### `templates/`

This folder stores the HTML pages.

HTML is the structure of the page.
It decides what appears on screen:

- headings
- forms
- buttons
- cards
- text

### `templates/base.html`

This is the shared layout file.

Instead of writing the top part of the page again and again, we keep common things here, like:

- page structure
- navigation links
- shared design layout

This helps us avoid repeating code.

### `templates/index.html`

This is the submit page.

This is the page where the student:

- types the item name
- writes the description
- chooses where it was found
- selects the date
- uploads a photo
- clicks the submit button

So this is the "input" page.

### `templates/items.html`

This is the listings page.

After data is saved, this page shows all saved items.
So this is the "output" page where students can see the result of their work.

### `static/`

This folder stores files that are not Python code and are not changing by themselves.

In simple words, it stores website assets.

Examples:

- CSS files
- images
- uploaded photos

### `static/style.css`

This file controls how the app looks.

It handles things like:

- colors
- spacing
- fonts
- button style
- card design
- responsive layout

Without this file, the app would still work, but it would look plain.

### `static/uploads/`

This folder stores the images uploaded by the user.

When someone submits a photo in the form, Flask saves that image here.

### `data/`

This folder stores saved app data.

Right now we are not using a database, so we need some place to keep item information.
That is why this folder exists.

### `data/items.json`

This file stores the found-item data.

Each saved item includes things like:

- item name
- description
- where it was found
- date
- photo filename
- time it was saved

This is temporary storage for learning.
Later, this can be replaced with a real database.

### `pyproject.toml`

This file tells Python and `uv` about the project.

It contains things like:

- project name
- Python version
- package dependencies

If the project needs Flask, that information is written here.

## What each folder is for

- `templates/` is for HTML pages
- `static/` is for CSS and image files
- `data/` is for saved item data

## Frontend and backend in very simple words

These are 2 words students hear a lot, so here is a simple meaning.

### Frontend

Frontend means the part the user sees and clicks in the browser.

In this project, frontend includes:

- the form
- the buttons
- the page design
- the item cards
- the text shown on screen

Most frontend code here is inside:

- `templates/`
- `static/`

### Backend

Backend means the part working behind the scenes.

The backend:

- receives data
- saves data
- loads data
- decides which page to show

Most backend code here is inside:

- `app.py`

## How the whole app works

Here is the story of what happens from start to finish.

### When the app first opens

1. The browser goes to `/`
2. Flask matches that route in `app.py`
3. Flask sends back `templates/index.html`
4. The browser shows the submit page

### When the student fills the form

The student enters:

- item name
- description
- location
- date
- photo

Then the student clicks the submit button.

### What happens after clicking submit

1. The form sends the data to Flask
2. `app.py` receives that data
3. Flask checks if all fields are filled
4. Flask checks if the uploaded file is an image
5. The photo is saved inside `static/uploads/`
6. The item details are saved inside `data/items.json`
7. Flask redirects the user to `/items`
8. The listings page loads and shows the saved item

This is a very important web development idea:

- the browser collects the data
- the server processes the data
- the server sends a new page back

## What is JSON in this project?

JSON is a simple text format used for storing data in a structured way.

You can think of it like a neat notebook for the app.
Instead of writing one sentence after another randomly, JSON stores data in a clean organized form.

In this project, `data/items.json` keeps all submitted items.

This is useful because:

- it is easy to read
- it is easy to save
- it is easier for beginners than setting up a database

Later, when students learn databases, this file can be replaced.

## What happens when you submit an item

- the photo is saved inside `static/uploads/`
- the item details are saved inside `data/items.json`
- the app redirects to the items page
- the item appears on the listings page

## Useful routes

- `/` -> submit item page
- `/items` -> listings page
- `/submit` -> route that receives the form data and saves it

## Run the tests

```bash
uv run python -m unittest discover -s tests
```

## Notes for class

- This version uses local file storage to keep things simple.
- This is good for learning because students can see where the data is going.
- In a later class, this can be upgraded to use a real database.
- The code is intentionally small and readable for beginners.
- `uv` makes Python project setup easier.
