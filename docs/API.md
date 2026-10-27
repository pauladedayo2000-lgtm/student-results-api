# API Documentation

Interactive docs are generated automatically while the server runs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Every endpoint requires HTTP Basic authentication.

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| POST | /students | Add a student | 201 | 401, 409, 422 |
| GET | /students | List students | 200 | 401 |
| GET | /students/{id}/results | One student's results and average | 200 | 401, 404 |
| GET | /students/{id}/average | Student average (%) | 200 | 401, 404 |
| POST | /subjects | Add a subject | 201 | 401, 409, 422 |
| GET | /subjects | List subjects | 200 | 401 |
| GET | /subjects/{id}/average | Subject average (%) | 200 | 401, 404 |
| POST | /assessments | Add an assessment | 201 | 401, 404, 422 |
| GET | /assessments | List assessments | 200 | 401 |
| GET | /assessments/{id}/average | Assessment average (%) | 200 | 401, 404 |
| POST | /scores | Add a score | 201 | 401, 404, 409, 422 |
| PUT | /scores/{id} | Update a score | 200 | 401, 404, 422 |

## Validation rules
- `full_name`: 2 to 100 characters.
- `student_code`: 3 to 20 characters, capital letters, digits and hyphens only (example `STU-001`).
- `name` (subject): 2 to 80 characters. `name` (assessment): 2 to 80 characters.
- `max_score`: greater than 0 and at most 1000.
- `value` (score): 0 or more, and never above the assessment's `max_score`.
- Unknown fields in a request body are rejected.

## How averages work
Each score becomes a percentage: `score / max_score * 100`. The average is the mean of those percentages, rounded to 2 decimals. This keeps a 15/20 quiz and a 82/100 test comparable.
If nothing has been scored yet, `average_percentage` is `null`.
