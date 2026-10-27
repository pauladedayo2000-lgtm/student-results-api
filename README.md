# Student Results API

A FastAPI service for managing subjects, assessments and student scores. You can add scores, update results, calculate averages and retrieve a student's full results.

## Features
- Students, subjects, assessments and scores stored in SQLite
- Pydantic validation on every request body
- HTTP Basic authentication on every endpoint
- Consistent JSON error responses
- Averages per student, subject and assessment
- Postman collection and sample JSON included

## Project structure
```
app/
  main.py        Routes and error handlers
  schemas.py     Pydantic validation models
  models.py      Database tables
  auth.py        Basic authentication
  database.py    Database connection
docs/
  API.md         Endpoint reference
  SAMPLES.md     Sample requests and responses
postman/         Postman collection
tests/           Automated test
```

## Setup
```bash
git clone <your-repo-url>
cd student-results-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Login
Default credentials: username `teacher`, password `change-me-123`.
Change them before you share the service:
```bash
export API_USERNAME=myname
export API_PASSWORD=a-long-secret-password
```
(Windows PowerShell: `$env:API_USERNAME="myname"`)

## Try it
1. Import `postman/student-results-api.postman_collection.json` into Postman.
2. Run the requests in order, 1 to 12. The login is already set at collection level.
3. Run the three `ERROR` requests to see the error responses.

## Run the test
```bash
python -m pytest -q
```

## How authentication, validation and error responses protect student results

**Authentication protects privacy.** Student scores are personal data. Every route, including the read-only ones, demands a username and password. A request without valid credentials gets a 401 and sees no data. The password check uses `secrets.compare_digest`, which takes the same time for a right or wrong guess and so gives an attacker no timing clues. Credentials come from environment variables, so they never sit in the source code. Basic authentication sends the password in a readable (Base64) form, so a real deployment must run behind HTTPS.

**Validation protects accuracy.** Pydantic models check each request before any code touches the database. A name that is too short, a negative score, a malformed student code or an extra unknown field is rejected with a 422. The API also checks that a score never exceeds the assessment's maximum, so a typo such as 780 instead of 78 cannot reach a student's record. A unique rule stops the same student receiving two scores for one assessment, which would distort averages. Because the update route uses the same rules, a later correction is held to the same standard.

**Clear error responses protect both.** Each failure returns a status code, an error label and a message that names the problem: 401 for bad login, 404 for a missing student, 409 for a duplicate, 422 for bad input. The teacher can fix a mistake quickly, which keeps results correct. The messages list field names and rules but never repeat submitted values, and they never reveal stack traces or database details. A caller learns what went wrong without learning anything about other students.

## Limitations
- One shared login, no separate roles (a teacher and a student would need different permissions).
- SQLite suits learning and small use. A production system would use PostgreSQL.
- No delete endpoints, to avoid accidental loss of results.
