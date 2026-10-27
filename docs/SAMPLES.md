# Sample Requests and Responses

All requests need Basic authentication. Default login: `teacher` / `change-me-123`.

## 1. Add a student
`POST /students`
```json
{ "full_name": "Amina Yusuf", "student_code": "STU-001" }
```
Response `201 Created`
```json
{ "id": 1, "full_name": "Amina Yusuf", "student_code": "STU-001" }
```

## 2. Add a subject
`POST /subjects`
```json
{ "name": "Mathematics" }
```
Response `201 Created`
```json
{ "id": 1, "name": "Mathematics" }
```

## 3. Add an assessment
`POST /assessments`
```json
{ "subject_id": 1, "name": "Midterm Test", "max_score": 100 }
```
Response `201 Created`
```json
{ "id": 1, "subject_id": 1, "name": "Midterm Test", "max_score": 100.0 }
```

## 4. Add a score
`POST /scores`
```json
{ "student_id": 1, "assessment_id": 1, "value": 78.5 }
```
Response `201 Created`
```json
{ "id": 1, "student_id": 1, "assessment_id": 1, "value": 78.5 }
```

## 5. Update a score
`PUT /scores/1`
```json
{ "value": 82 }
```
Response `200 OK`
```json
{ "id": 1, "student_id": 1, "assessment_id": 1, "value": 82.0 }
```

## 6. Get a student's results
`GET /students/1/results`

Response `200 OK`
```json
{
  "student": { "id": 1, "full_name": "Amina Yusuf", "student_code": "STU-001" },
  "results": [
    {
      "score_id": 1,
      "subject": "Mathematics",
      "assessment": "Midterm Test",
      "score": 82.0,
      "max_score": 100.0,
      "percentage": 82.0
    }
  ],
  "average_percentage": 82.0
}
```

## 7. Calculate averages
`GET /students/1/average`, `GET /subjects/1/average`, `GET /assessments/1/average`

Response `200 OK`
```json
{ "id": 1, "name": "Amina Yusuf", "scores_counted": 1, "average_percentage": 82.0 }
```

## Error responses

Missing or wrong login, `401 Unauthorized`
```json
{ "error": "unauthorized", "message": "Invalid username or password." }
```

Invalid body, `422 Unprocessable Entity`
```json
{
  "error": "validation_error",
  "details": [
    { "field": "full_name", "message": "String should have at least 2 characters" },
    { "field": "student_code", "message": "String should match pattern '^[A-Z0-9-]{3,20}$'" }
  ]
}
```

Score above the maximum, `422 Unprocessable Entity`
```json
{ "error": "validation_error", "message": "Score 150.0 is higher than the maximum of 100.0 for 'Midterm Test'." }
```

Student does not exist, `404 Not Found`
```json
{ "error": "not_found", "message": "Student 999 not found." }
```

Duplicate score, `409 Conflict`
```json
{ "error": "conflict", "message": "This student already has a score for this assessment (score id 1). Use PUT /scores/1 to change it." }
```
