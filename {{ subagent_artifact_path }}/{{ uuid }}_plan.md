# Class 5 Plan

## Goal

Add simple Class 5 features to the Flask lost-and-found app:

- add a `contact` field for phone number or email
- use OpenAI to read the uploaded image
- auto-fill item details from the image in a simple way
- keep the app easy for students to understand
- create a new `class5-README.md` without replacing the older README files

## Recommended Approach

Keep the current two-page flow:

- `/` stays the add item page
- `/items` stays the items list page

Use a very small AI flow:

- student uploads an image on the add page
- student clicks a small `Auto Fill With AI` button
- Flask uploads the image to Cloudinary first
- Flask sends the hosted image URL to OpenAI
- OpenAI returns simple JSON with fields like `name`, `description`, and `found_location`
- Flask sends those values back to the page
- the form fields get filled automatically
- student can still edit the text before saving

This keeps the app simple and matches the user request better than generating the text only after save.

## Files To Change

- `/Users/mohithkumar/Desktop/flask/app.py`
- `/Users/mohithkumar/Desktop/flask/templates/index.html`
- `/Users/mohithkumar/Desktop/flask/templates/items.html`
- `/Users/mohithkumar/Desktop/flask/tests/test_app.py`
- `/Users/mohithkumar/Desktop/flask/pyproject.toml`
- `/Users/mohithkumar/Desktop/flask/.env.example`
- `/Users/mohithkumar/Desktop/flask/.env`
- `/Users/mohithkumar/Desktop/flask/class5-README.md`

## Backend Changes

1. Add `contact` to the `Item` model in `app.py`.
2. Add a small helper to check if the OpenAI key exists.
3. Add a helper that uploads the chosen image to Cloudinary and returns a URL.
4. Add a helper that sends the image URL to OpenAI and asks for very short structured data:
   - `name`
   - `description`
   - `found_location`
   - optional `category`
5. Add a new route like `POST /autofill`:
   - accept uploaded image
   - validate image
   - require Cloudinary + OpenAI keys
   - upload image to Cloudinary
   - call OpenAI vision
   - return JSON with suggested values and the image URL
6. Keep `/submit` as the final save route:
   - accept normal fields
   - accept `contact`
   - require a photo or a previously generated `photo_url`
   - save the item to the database
7. Update `/items/<item_id>/edit` to support editing `contact`.

## Frontend Changes

### `index.html`

- keep the form simple
- add a `contact` input with one label like `Contact (phone or email)`
- add one small `Auto Fill With AI` button near the photo input
- add a hidden field for `photo_url`
- add very small JavaScript:
  - send the image to `/autofill`
  - receive JSON
  - put AI values into the form
  - keep the form editable
  - show a small message if AI fails

### `items.html`

- show `contact` in each item card
- add `contact` to the edit modal
- optionally show an `AI Note` only if the code stores one, but skip this if it adds clutter

## Data Design

Keep the database simple. Recommended fields:

- `id`
- `name`
- `description`
- `found_location`
- `found_date`
- `contact`
- `photo_url`
- `created_at`

Do not add too many AI-specific columns in the first version.

## OpenAI Design

Use the OpenAI API with a very small prompt asking for beginner-friendly structured output.

Recommended behavior:

- if AI succeeds, fill the form
- if AI fails, show a soft error and let the student fill the form manually
- do not block the whole app because AI is an extra feature

## Simplicity Rules

- keep logic mostly inside `app.py`
- use only a few helper functions with clear names
- avoid adding migrations or advanced architecture
- add clear comments only where needed
- prefer simple validation messages

## Documentation Changes

Create `/Users/mohithkumar/Desktop/flask/class5-README.md` and explain:

- the new `contact` field
- OpenAI API key
- what AI autofill means
- how the image is read
- what Cloudinary still does
- what environment variables do
- how external APIs work
- how the autofill route works
- code snippets for the new AI flow

Do not replace `class4-README.md`.

## Verification

1. Run dependency install.
2. Run the Flask app.
3. Test manual upload and save.
4. Test AI autofill from image.
5. Edit the auto-filled values and save.
6. Confirm `/items` shows contact info.
7. Edit and delete still work.
8. Run the unit tests.
9. Add or update tests for:
   - contact field save
   - AI autofill JSON response
   - final submit after autofill
   - edit contact field

