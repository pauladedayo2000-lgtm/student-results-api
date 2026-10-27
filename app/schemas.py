from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    """Trim spaces and reject any field we did not define."""
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class StudentCreate(Strict):
    full_name: str = Field(min_length=2, max_length=100, examples=["Amina Yusuf"])
    student_code: str = Field(pattern=r"^[A-Z0-9-]{3,20}$", examples=["STU-001"])


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    student_code: str


class SubjectCreate(Strict):
    name: str = Field(min_length=2, max_length=80, examples=["Mathematics"])


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class AssessmentCreate(Strict):
    subject_id: int = Field(gt=0, examples=[1])
    name: str = Field(min_length=2, max_length=80, examples=["Midterm Test"])
    max_score: float = Field(gt=0, le=1000, examples=[100])


class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    name: str
    max_score: float


class ScoreCreate(Strict):
    student_id: int = Field(gt=0, examples=[1])
    assessment_id: int = Field(gt=0, examples=[1])
    value: float = Field(ge=0, examples=[78.5])


class ScoreUpdate(Strict):
    value: float = Field(ge=0, examples=[82])


class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    assessment_id: int
    value: float


class ResultItem(BaseModel):
    score_id: int
    subject: str
    assessment: str
    score: float
    max_score: float
    percentage: float


class StudentResults(BaseModel):
    student: StudentOut
    results: list[ResultItem]
    average_percentage: float | None


class AverageOut(BaseModel):
    id: int
    name: str
    scores_counted: int
    average_percentage: float | None
