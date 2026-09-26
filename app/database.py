import os
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, User, WorkoutPlan

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")

# SQLite requires check_same_thread=False for FastAPI concurrency
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes the database and creates all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------
# Core CRUD Operations as specified in Activity 2.1 & 3.1
# -------------------------------------------------------------

def save_user(db: Session, user_data: dict) -> User:
    """
    Saves a new user or updates an existing user by user_id.
    """
    existing_user = db.query(User).filter(User.user_id == user_data.get("user_id")).first()
    if existing_user:
        existing_user.username = user_data.get("username", existing_user.username)
        existing_user.age = user_data.get("age", existing_user.age)
        existing_user.weight = user_data.get("weight", existing_user.weight)
        existing_user.goal = user_data.get("goal", existing_user.goal)
        existing_user.intensity = user_data.get("intensity", existing_user.intensity)
        db.commit()
        db.refresh(existing_user)
        return existing_user

    user = User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        age=user_data["age"],
        weight=user_data["weight"],
        goal=user_data["goal"],
        intensity=user_data["intensity"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(db: Session, user_id: str, original_plan: str, nutrition_tip: Optional[str] = None) -> WorkoutPlan:
    """
    Saves a new workout plan or updates an existing original plan for a user.
    """
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    if plan:
        plan.original_plan = original_plan
        if nutrition_tip:
            plan.nutrition_tip = nutrition_tip
        db.commit()
        db.refresh(plan)
        return plan

    new_plan = WorkoutPlan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan


def update_plan(db: Session, user_id: str, updated_plan: str, feedback: str) -> Optional[WorkoutPlan]:
    """
    Updates the plan record with the AI feedback-revised plan and user feedback text.
    """
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    if not plan:
        return None

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    db.commit()
    db.refresh(plan)
    return plan


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Retrieves a user by user_id."""
    return db.query(User).filter(User.user_id == user_id).first()


def get_original_plan(db: Session, user_id: str) -> Optional[WorkoutPlan]:
    """Retrieves the workout plan record for a given user_id."""
    return db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()


def get_all_users(db: Session) -> List[User]:
    """Retrieves all registered users ordered by registration date descending."""
    return db.query(User).order_by(User.created_at.desc()).all()


def get_all_plans(db: Session) -> List[WorkoutPlan]:
    """Retrieves all workout plan records."""
    return db.query(WorkoutPlan).all()


def delete_user(db: Session, user_id: str) -> bool:
    """Deletes a user and their associated plans by user_id."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
