from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import models, schemas
from .auth import require_user
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Student Results API",
    description="Manage subjects, assessments and student scores. "
    "Every endpoint requires HTTP Basic authentication.",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(require_user)],  # protects every route
)

# ---------- Clear, consistent error responses ----------

ERROR_CODES = {400: "bad_request", 401: "unauthorized", 404: "not_found",
               405: "method_not_allowed", 409: "conflict", 422: "validation_error"}


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": ERROR_CODES.get(exc.status_code, "error"), "message": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    # We list the field and the problem, but never echo the submitted values back.
    details = [
        {"field": ".".join(str(p) for p in e["loc"] if p != "body"), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"error": "validation_error", "details": details})


# ---------- Helpers ----------

def get_or_404(db: Session, model, item_id: int, label: str):
    item = db.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{label} {item_id} not found.")
    return item


def percent(score: float, max_score: float) -> float:
    return round(score / max_score * 100, 2)


def average_of(percentages: list[float]) -> float | None:
    return round(sum(percentages) / len(percentages), 2) if percentages else None


# ---------- Students ----------

@app.post("/students", response_model=schemas.StudentOut, status_code=201, tags=["Students"])
def create_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Student).where(models.Student.student_code == data.student_code)):
        raise HTTPException(409, f"Student code {data.student_code} already exists.")
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.get("/students", response_model=list[schemas.StudentOut], tags=["Students"])
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(models.Student)).all()


@app.get("/students/{student_id}/results", response_model=schemas.StudentResults, tags=["Students"])
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    student = get_or_404(db, models.Student, student_id, "Student")
    results = [
        schemas.ResultItem(
            score_id=s.id,
            subject=s.assessment.subject.name,
            assessment=s.assessment.name,
            score=s.value,
            max_score=s.assessment.max_score,
            percentage=percent(s.value, s.assessment.max_score),
        )
        for s in student.scores
    ]
    return schemas.StudentResults(
        student=student, results=results,
        average_percentage=average_of([r.percentage for r in results]),
    )


@app.get("/students/{student_id}/average", response_model=schemas.AverageOut, tags=["Averages"])
def student_average(student_id: int, db: Session = Depends(get_db)):
    student = get_or_404(db, models.Student, student_id, "Student")
    pcts = [percent(s.value, s.assessment.max_score) for s in student.scores]
    return schemas.AverageOut(id=student.id, name=student.full_name,
                              scores_counted=len(pcts), average_percentage=average_of(pcts))


# ---------- Subjects ----------

@app.post("/subjects", response_model=schemas.SubjectOut, status_code=201, tags=["Subjects"])
def create_subject(data: schemas.SubjectCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Subject).where(models.Subject.name == data.name)):
        raise HTTPException(409, f"Subject '{data.name}' already exists.")
    subject = models.Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@app.get("/subjects", response_model=list[schemas.SubjectOut], tags=["Subjects"])
def list_subjects(db: Session = Depends(get_db)):
    return db.scalars(select(models.Subject)).all()


@app.get("/subjects/{subject_id}/average", response_model=schemas.AverageOut, tags=["Averages"])
def subject_average(subject_id: int, db: Session = Depends(get_db)):
    subject = get_or_404(db, models.Subject, subject_id, "Subject")
    pcts = [percent(s.value, a.max_score) for a in subject.assessments for s in a.scores]
    return schemas.AverageOut(id=subject.id, name=subject.name,
                              scores_counted=len(pcts), average_percentage=average_of(pcts))


# ---------- Assessments ----------

@app.post("/assessments", response_model=schemas.AssessmentOut, status_code=201, tags=["Assessments"])
def create_assessment(data: schemas.AssessmentCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Subject, data.subject_id, "Subject")
    assessment = models.Assessment(**data.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@app.get("/assessments", response_model=list[schemas.AssessmentOut], tags=["Assessments"])
def list_assessments(db: Session = Depends(get_db)):
    return db.scalars(select(models.Assessment)).all()


@app.get("/assessments/{assessment_id}/average", response_model=schemas.AverageOut, tags=["Averages"])
def assessment_average(assessment_id: int, db: Session = Depends(get_db)):
    a = get_or_404(db, models.Assessment, assessment_id, "Assessment")
    pcts = [percent(s.value, a.max_score) for s in a.scores]
    return schemas.AverageOut(id=a.id, name=a.name,
                              scores_counted=len(pcts), average_percentage=average_of(pcts))


# ---------- Scores ----------

def check_within_max(value: float, assessment: models.Assessment):
    if value > assessment.max_score:
        raise HTTPException(
            422, f"Score {value} is higher than the maximum of {assessment.max_score} "
                 f"for '{assessment.name}'.")


@app.post("/scores", response_model=schemas.ScoreOut, status_code=201, tags=["Scores"])
def add_score(data: schemas.ScoreCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Student, data.student_id, "Student")
    assessment = get_or_404(db, models.Assessment, data.assessment_id, "Assessment")
    check_within_max(data.value, assessment)
    existing = db.scalar(select(models.Score).where(
        models.Score.student_id == data.student_id,
        models.Score.assessment_id == data.assessment_id))
    if existing:
        raise HTTPException(
            409, f"This student already has a score for this assessment (score id {existing.id}). "
                 f"Use PUT /scores/{existing.id} to change it.")
    score = models.Score(student_id=data.student_id, assessment_id=data.assessment_id, value=data.value)
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@app.put("/scores/{score_id}", response_model=schemas.ScoreOut, tags=["Scores"])
def update_score(score_id: int, data: schemas.ScoreUpdate, db: Session = Depends(get_db)):
    score = get_or_404(db, models.Score, score_id, "Score")
    check_within_max(data.value, score.assessment)
    score.value = data.value
    db.commit()
    db.refresh(score)
    return score
