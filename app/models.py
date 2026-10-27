from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    student_code: Mapped[str] = mapped_column(String(20), unique=True)
    scores: Mapped[list["Score"]] = relationship(back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="subject")


class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    name: Mapped[str] = mapped_column(String(80))
    max_score: Mapped[float] = mapped_column(Float)
    subject: Mapped[Subject] = relationship(back_populates="assessments")
    scores: Mapped[list["Score"]] = relationship(back_populates="assessment")


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (UniqueConstraint("student_id", "assessment_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"))
    value: Mapped[float] = mapped_column(Float)
    student: Mapped[Student] = relationship(back_populates="scores")
    assessment: Mapped[Assessment] = relationship(back_populates="scores")
