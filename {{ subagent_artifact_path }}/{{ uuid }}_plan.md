# Lost Item Match Plan

## Goal

Add a new page where a student can report a lost item and get AI-assisted suggested matches from the found items already saved in the app.

## Recommended Approach

Keep the current found-item flow as it is:

- `/` for reporting a found item
- `/items` for viewing found items

Add one new lost-item workflow:

- `/lost-report` shows a simple form
- `/lost-report/matches` checks the report and shows possible found-item matches

To keep the code easy to understand:

- do not add a new saved database table for lost reports in version 1
- use the lost report only as temporary form data
- use AI only to normalize and clean the lost report
- use simple Python scoring to rank matches against saved found items

## Files To Change

- `/Users/mohithkumar/Desktop/flask/app.py`
- `/Users/mohithkumar/Desktop/flask/templates/base.html`
- `/Users/mohithkumar/Desktop/flask/templates/lost_report.html`
- `/Users/mohithkumar/Desktop/flask/templates/match_results.html`
- `/Users/mohithkumar/Desktop/flask/tests/test_app.py`
- `/Users/mohithkumar/Desktop/flask/class5-README.md`
- `/Users/mohithkumar/Desktop/flask/.env.example`

## Backend Changes

### `app.py`

Add a small set of new helpers:

- `normalize_lost_report_with_ai(form_data)`
- `extract_keywords(text)`
- `score_match(lost_report, item)`
- `find_suggested_matches(lost_report)`

Add new routes:

- `GET /lost-report`
- `POST /lost-report/matches`

Recommended route flow:

1. student opens `/lost-report`
2. student fills lost item details
3. Flask validates the form
4. Flask optionally uses OpenAI to normalize the text
5. Flask compares the lost report with saved `Item` rows
6. Flask sorts matches by score
7. Flask renders a results page with top matches

## Matching Logic

Use easy-to-read rule-based scoring first:

- item name similarity
- description keyword overlap
- similar location
- same or nearby date
- optional color/category match if AI extracts them

Keep the matching simple and readable inside Python.

Example scoring idea:

- `+4` for very similar name
- `+2` for keyword overlap
- `+2` for same location
- `+1` for same date

Only show the best 3 to 5 results.

## AI Usage

Use OpenAI to normalize the lost report into structured fields, not to search the whole database directly.

Suggested structured fields:

- `name`
- `normalized_description`
- `category`
- `color`
- `keywords`

If AI fails or the key is missing:

- fall back to plain text matching
- still show results if possible

This keeps the feature useful even without AI.

## Template Changes

### `base.html`

Add a new navigation link:

- `Report Lost Item`

### `lost_report.html`

Create a simple form with:

- name
- description
- lost location
- lost date
- contact
- optional photo

Submit button:

- `Find Possible Matches`

### `match_results.html`

Show:

- the lost-item summary
- AI-normalized summary if available
- top suggested found-item matches
- contact details from found items
- empty state if nothing matches well

## Tests

Extend `tests/test_app.py` with:

- lost report page loads
- valid lost report returns results page
- similar found item appears in the matches
- no-match case shows a safe message
- AI failure falls back to normal matching

Keep mocking style similar to the current Cloudinary/OpenAI tests.

## Documentation

Update `class5-README.md` to explain:

- the new lost-item page
- how AI matching works
- the difference between AI autofill and AI matching
- how fallback matching works without AI
- new route examples and page flow

Update `.env.example` to document:

- `OPENAI_VISION_MODEL`
- optional `OPENAI_MATCH_MODEL` if a separate model is used

## Verification

1. Run `uv sync`
2. Run `uv run python app.py`
3. Open the found-item page and save some sample found items
4. Open `/lost-report`
5. Submit a lost report similar to one of the found items
6. Confirm matching results appear
7. Confirm the app still works when AI matching is mocked or unavailable
8. Run `uv run python -m unittest discover -s tests`

