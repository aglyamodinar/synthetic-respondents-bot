from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    telegram_user_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(2), default="ru")
    mode: Mapped[str] = mapped_column(String(20), default="pilot")
    question_text: Mapped[str] = mapped_column(Text)
    segments: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    stimuli: Mapped[list["Stimulus"]] = relationship("Stimulus", back_populates="study")
    runs: Mapped[list["Run"]] = relationship("Run", back_populates="study")


class Stimulus(Base):
    __tablename__ = "stimuli"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id", ondelete="CASCADE"), index=True)
    stimulus_id: Mapped[str] = mapped_column(String(64))
    stimulus_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(20), default="other")
    language: Mapped[str] = mapped_column(String(2), default="ru")

    study: Mapped["Study"] = relationship("Study", back_populates="stimuli")
    responses: Mapped[list["SyntheticResponse"]] = relationship(
        "SyntheticResponse", back_populates="stimulus"
    )
    metrics: Mapped[list["Metric"]] = relationship("Metric", back_populates="stimulus")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id", ondelete="CASCADE"), index=True)
    model_name: Mapped[str] = mapped_column(String(100))
    respondent_count: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="queued")
    token_input: Mapped[int] = mapped_column(Integer, default=0)
    token_output: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    study: Mapped["Study"] = relationship("Study", back_populates="runs")
    responses: Mapped[list["SyntheticResponse"]] = relationship("SyntheticResponse", back_populates="run")
    metrics: Mapped[list["Metric"]] = relationship("Metric", back_populates="run")
    artifacts: Mapped[list["Artifact"]] = relationship("Artifact", back_populates="run")


class SyntheticResponse(Base):
    __tablename__ = "synthetic_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    stimulus_pk: Mapped[int] = mapped_column(ForeignKey("stimuli.id", ondelete="CASCADE"), index=True)
    segment_key: Mapped[str] = mapped_column(String(100), default="all")
    respondent_idx: Mapped[int] = mapped_column(Integer)
    response_text: Mapped[str] = mapped_column(Text)
    pmf: Mapped[list] = mapped_column(JSONB)
    expected_score: Mapped[float] = mapped_column(Float)

    run: Mapped["Run"] = relationship("Run", back_populates="responses")
    stimulus: Mapped["Stimulus"] = relationship("Stimulus", back_populates="responses")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    stimulus_pk: Mapped[int] = mapped_column(ForeignKey("stimuli.id", ondelete="CASCADE"), index=True)
    segment_key: Mapped[str] = mapped_column(String(100), default="all")

    mean: Mapped[float] = mapped_column(Float)
    median: Mapped[float] = mapped_column(Float)
    sd: Mapped[float] = mapped_column(Float)
    variance: Mapped[float] = mapped_column(Float)
    mode: Mapped[float] = mapped_column(Float)
    top2box: Mapped[float] = mapped_column(Float)
    bottom2box: Mapped[float] = mapped_column(Float)
    topbox: Mapped[float] = mapped_column(Float)
    net_score: Mapped[float] = mapped_column(Float)
    distribution: Mapped[dict] = mapped_column(JSONB)
    ci_mean_low: Mapped[float] = mapped_column(Float)
    ci_mean_high: Mapped[float] = mapped_column(Float)
    ci_t2b_low: Mapped[float] = mapped_column(Float)
    ci_t2b_high: Mapped[float] = mapped_column(Float)

    run: Mapped["Run"] = relationship("Run", back_populates="metrics")
    stimulus: Mapped["Stimulus"] = relationship("Stimulus", back_populates="metrics")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(30), default="pdf")
    path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run: Mapped["Run"] = relationship("Run", back_populates="artifacts")

