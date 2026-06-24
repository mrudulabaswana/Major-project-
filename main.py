from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ── Database setup ───────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FeedbackModel(Base):
    __tablename__ = "feedback"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    email      = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    department = Column(String, default="")
    semester   = Column(String, default="")
    phone      = Column(String, nullable=True)
    message    = Column(String, nullable=False)
    rating     = Column(Integer, nullable=False)
    category   = Column(String, nullable=False)
    sub_reason = Column(String, nullable=False)
    status     = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ── Pydantic schemas ─────────────────────────────────────────────────────────
class FeedbackCreate(BaseModel):
    name: str
    email: str
    student_id: str
    department: Optional[str] = ""
    semester: Optional[str] = ""
    phone: Optional[str] = None
    message: str
    rating: int
    category: str
    sub_reason: str

class FeedbackOut(BaseModel):
    id: int
    name: str
    email: str
    student_id: str
    department: str
    semester: str
    phone: Optional[str]
    message: str
    rating: int
    category: str
    sub_reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str

class CategoryCount(BaseModel):
    category: str
    count: int

class StatusCount(BaseModel):
    status: str
    count: int

class StatsOut(BaseModel):
    total: int
    average_rating: float
    recent_count: int
    by_category: List[CategoryCount]
    by_status: List[StatusCount]

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Student Management System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends
from sqlalchemy.orm import Session

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/api/feedback", response_model=List[FeedbackOut])
def list_feedback(
    category: Optional[str] = Query(None),
    rating: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(FeedbackModel)
    if category:
        q = q.filter(FeedbackModel.category == category)
    if rating:
        q = q.filter(FeedbackModel.rating == rating)
    if status:
        q = q.filter(FeedbackModel.status == status)
    return q.order_by(desc(FeedbackModel.created_at)).all()


@app.post("/api/feedback", response_model=FeedbackOut, status_code=201)
def create_feedback(body: FeedbackCreate, db: Session = Depends(get_db)):
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    row = FeedbackModel(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/feedback/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(FeedbackModel).count()
    avg = db.query(func.avg(FeedbackModel.rating)).scalar() or 0.0

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent = db.query(FeedbackModel).filter(FeedbackModel.created_at >= seven_days_ago).count()

    by_cat = (
        db.query(FeedbackModel.category, func.count().label("count"))
        .group_by(FeedbackModel.category)
        .all()
    )
    by_status = (
        db.query(FeedbackModel.status, func.count().label("count"))
        .group_by(FeedbackModel.status)
        .all()
    )

    return StatsOut(
        total=total,
        average_rating=round(float(avg), 2),
        recent_count=recent,
        by_category=[CategoryCount(category=r[0], count=r[1]) for r in by_cat],
        by_status=[StatusCount(status=r[0], count=r[1]) for r in by_status],
    )


@app.get("/api/feedback/{feedback_id}", response_model=FeedbackOut)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    row = db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return row


@app.patch("/api/feedback/{feedback_id}/status", response_model=FeedbackOut)
def update_status(feedback_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    valid = {"new", "reviewed", "resolved"}
    if body.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    row = db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Feedback not found")
    row.status = body.status
    db.commit()
    db.refresh(row)
    return row


@app.delete("/api/feedback/{feedback_id}", status_code=204)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    row = db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(row)
    db.commit()


@app.get("/api/healthz")
def health():
    return {"status": "ok"}
