import os
from typing import Optional
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import (
    get_db, 
    save_user, 
    save_plan, 
    update_plan, 
    get_user, 
    get_original_plan, 
    get_all_users, 
    get_all_plans,
    delete_user
)
from app.models import UserInput, FeedbackRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan

# Set up templates directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter()


# -------------------------------------------------------------
# 1. Home Route: Serves the input form (index.html)
# -------------------------------------------------------------
@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    """
    Renders the FitBuddy homepage with user input form.
    """
    api_configured = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "title": "FitBuddy – AI Fitness Plan Generator",
            "api_configured": api_configured
        }
    )


# -------------------------------------------------------------
# 2. Generate Workout Route: Processes form input and generates AI plan
# -------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Captures user details, invokes Gemini AI models, persists records, and displays results.
    """
    try:
        user_input = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            weight=weight,
            goal=goal.strip(),
            intensity=intensity.strip()
        )
    except Exception as validation_err:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error_message": f"Validation Error: {validation_err}",
                "form_data": {
                    "username": username,
                    "user_id": user_id,
                    "age": age,
                    "weight": weight,
                    "goal": goal,
                    "intensity": intensity
                }
            },
            status_code=400
        )

    user_dict = user_input.model_dump()

    # 1. Generate 7-Day Workout Plan via Gemini 1.5 Pro
    workout_plan = generate_workout_gemini(user_dict)

    # 2. Generate Goal-Specific Nutrition Tip via Gemini Flash
    nutrition_tip = generate_nutrition_tip_with_flash(user_input.goal, user_dict)

    # 3. Persist User and Plan in Database
    save_user(db, user_dict)
    save_plan(db, user_id=user_input.user_id, original_plan=workout_plan, nutrition_tip=nutrition_tip)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": user_input.username,
            "user_id": user_input.user_id,
            "age": user_input.age,
            "weight": user_input.weight,
            "goal": user_input.goal,
            "intensity": user_input.intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "is_updated": False,
            "status_message": "AI Fitness Plan Generated Successfully!"
        }
    )


# -------------------------------------------------------------
# 3. Submit Feedback Route: Updates workout plan with AI
# -------------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Captures user feedback, revises the plan via Gemini Pro, updates database, and re-renders.
    """
    clean_user_id = user_id.strip()
    clean_feedback = feedback.strip()

    user = get_user(db, clean_user_id)
    plan_record = get_original_plan(db, clean_user_id)

    if not plan_record or not user:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "error_message": f"No existing plan found for User ID '{clean_user_id}'. Please generate a plan first.",
                "user_id": clean_user_id,
                "username": clean_user_id,
                "age": "N/A",
                "weight": "N/A",
                "goal": "N/A",
                "intensity": "N/A",
                "workout_plan": "No plan found.",
                "nutrition_tip": "N/A",
                "is_updated": False
            },
            status_code=404
        )

    user_details = {
        "username": user.username,
        "user_id": user.user_id,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity
    }

    base_plan = plan_record.original_plan
    revised_plan = update_workout_plan(base_plan, clean_feedback, user_details)

    update_plan(db, user_id=clean_user_id, updated_plan=revised_plan, feedback=clean_feedback)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": revised_plan,
            "original_plan": plan_record.original_plan,
            "nutrition_tip": plan_record.nutrition_tip,
            "feedback": clean_feedback,
            "is_updated": True,
            "status_message": "Workout plan successfully updated with Gemini AI based on your feedback!"
        }
    )


# -------------------------------------------------------------
# 4. Admin View: Displays all users and their original & updated plans
# -------------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request, db: Session = Depends(get_db)):
    """
    Renders administrative view of all registered users and their workout plans.
    """
    users = get_all_users(db)
    plans = get_all_plans(db)

    plan_map = {plan.user_id: plan for plan in plans}

    users_data = []
    for u in users:
        p = plan_map.get(u.user_id)
        users_data.append({
            "user": u,
            "plan": p,
            "has_updated_plan": bool(p and p.updated_plan)
        })

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users_data": users_data,
            "total_users": len(users),
            "updated_count": sum(1 for item in users_data if item["has_updated_plan"])
        }
    )


# -------------------------------------------------------------
# 5. Delete User Route (Admin capability)
# -------------------------------------------------------------
@router.post("/delete-user/{user_id}")
@router.get("/delete-user/{user_id}")
async def remove_user(user_id: str, db: Session = Depends(get_db)):
    """
    Deletes a user and their plans, then redirects to admin dashboard.
    """
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)


# -------------------------------------------------------------
# 6. JSON API & Health Endpoints
# -------------------------------------------------------------
@router.get("/api/users")
async def api_get_users(db: Session = Depends(get_db)):
    """Returns all registered users and plans in JSON format."""
    users = get_all_users(db)
    plans = {p.user_id: p for p in get_all_plans(db)}
    result = []
    for u in users:
        p = plans.get(u.user_id)
        result.append({
            "user_id": u.user_id,
            "username": u.username,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "has_original_plan": bool(p and p.original_plan),
            "has_updated_plan": bool(p and p.updated_plan),
            "feedback": p.feedback if p else None
        })
    return {"status": "success", "count": len(result), "data": result}


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    api_key_set = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "app": "FitBuddy - AI Fitness Plan Generator",
        "gemini_api_configured": api_key_set,
        "database": "sqlite_connected"
    }
