from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """SQLAlchemy model for storing registered users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # One-to-one or one-to-many relationship with workout plans
    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', username='{self.username}', goal='{self.goal}')>"


class WorkoutPlan(Base):
    """SQLAlchemy model for storing workout plans, nutrition tips, and feedback."""
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="plans")

    def __repr__(self):
        return f"<WorkoutPlan(id={self.id}, user_id='{self.user_id}')>"


# -------------------------------------------------------------
# Pydantic Schemas for Validation
# -------------------------------------------------------------

class UserInput(BaseModel):
    """Pydantic schema for validating user input during workout generation."""
    username: str = Field(..., min_length=2, max_length=100, description="Name of the user")
    user_id: str = Field(..., min_length=2, max_length=50, description="Unique User identifier")
    age: int = Field(..., ge=10, le=120, description="Age in years")
    weight: float = Field(..., ge=20.0, le=350.0, description="Weight in kilograms")
    goal: str = Field(..., min_length=2, max_length=100, description="Fitness goal (e.g. Weight Loss, Muscle Gain)")
    intensity: str = Field(..., min_length=2, max_length=20, description="Workout intensity (Low, Medium, High)")


class FeedbackRequest(BaseModel):
    """Pydantic schema for validating feedback input for plan refinement."""
    user_id: str = Field(..., min_length=1, max_length=50, description="User ID to update plan for")
    feedback: str = Field(..., min_length=3, max_length=1000, description="Feedback or requested modifications")


class PlanResponse(BaseModel):
    """Pydantic schema for API responses."""
    user_id: str
    username: str
    age: int
    weight: float
    goal: str
    intensity: str
    original_plan: str
    updated_plan: Optional[str] = None
    nutrition_tip: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
