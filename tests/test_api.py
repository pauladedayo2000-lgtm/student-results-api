import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

AUTH = ("teacher", "change-me-123")


def setup_module(module):
    Base.metadata.drop_all(bind=engine)


def test_full_flow():
    with TestClient(app) as c:
        assert c.get("/students").status_code == 401
        assert c.get("/students", auth=("teacher", "wrong")).status_code == 401

        r = c.post("/students", json={"full_name": "Amina Yusuf", "student_code": "STU-001"}, auth=AUTH)
        assert r.status_code == 201, r.text
        assert c.post("/students", json={"full_name": "Amina Yusuf", "student_code": "STU-001"}, auth=AUTH).status_code == 409
        assert c.post("/students", json={"full_name": "A", "student_code": "bad code", "extra": 1}, auth=AUTH).status_code == 422

        assert c.post("/subjects", json={"name": "Mathematics"}, auth=AUTH).status_code == 201
        assert c.post("/subjects", json={"name": "English"}, auth=AUTH).status_code == 201
        assert c.post("/assessments", json={"subject_id": 1, "name": "Midterm", "max_score": 100}, auth=AUTH).status_code == 201
        assert c.post("/assessments", json={"subject_id": 2, "name": "Quiz 1", "max_score": 20}, auth=AUTH).status_code == 201
        assert c.post("/assessments", json={"subject_id": 99, "name": "Quiz", "max_score": 20}, auth=AUTH).status_code == 404

        assert c.post("/scores", json={"student_id": 1, "assessment_id": 1, "value": 78.5}, auth=AUTH).status_code == 201
        assert c.post("/scores", json={"student_id": 1, "assessment_id": 2, "value": 15}, auth=AUTH).status_code == 201
        assert c.post("/scores", json={"student_id": 1, "assessment_id": 1, "value": 50}, auth=AUTH).status_code == 409
        assert c.post("/scores", json={"student_id": 1, "assessment_id": 2, "value": 25}, auth=AUTH).status_code in (409, 422)
        assert c.post("/scores", json={"student_id": 1, "assessment_id": 1, "value": -5}, auth=AUTH).status_code == 422

        r = c.put("/scores/1", json={"value": 82}, auth=AUTH)
        assert r.status_code == 200 and r.json()["value"] == 82
        assert c.put("/scores/1", json={"value": 101}, auth=AUTH).status_code == 422
        assert c.put("/scores/99", json={"value": 10}, auth=AUTH).status_code == 404

        r = c.get("/students/1/results", auth=AUTH)
        print(r.json())
        assert r.json()["average_percentage"] == 78.5   # (82 + 75) / 2
        assert c.get("/students/1/average", auth=AUTH).json()["scores_counted"] == 2
        assert c.get("/subjects/1/average", auth=AUTH).json()["average_percentage"] == 82.0
        assert c.get("/assessments/2/average", auth=AUTH).json()["average_percentage"] == 75.0
        assert c.get("/students/99/results", auth=AUTH).status_code == 404
        print(c.post("/students", json={"full_name": "A", "student_code": "bad code"}, auth=AUTH).json())
        print(c.get("/students", auth=("x","y")).json())
