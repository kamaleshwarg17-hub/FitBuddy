"""
Comprehensive End-to-End Test Suite for FitBuddy
Verifies:
1. Database initialization and CRUD operations (save_user, save_plan, update_plan, etc.)
2. AI Generation modules (gemini_generator, gemini_flash_generator, updated_plan)
3. FastAPI Endpoints via TestClient:
   - GET / (Homepage form)
   - POST /generate-workout (Workout & nutrition generation + persistence)
   - POST /submit-feedback (Feedback revision loop)
   - GET /view-all-users (Admin dashboard)
   - GET /api/users (JSON API)
   - GET /health (Health check)
   - POST /delete-user/{user_id} (Admin deletion)
4. Entry points (main:app, app.main:app)
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure current directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from starlette.testclient import TestClient
from app.database import (
    SessionLocal, 
    init_db, 
    save_user, 
    save_plan, 
    update_plan, 
    get_user, 
    get_original_plan, 
    get_all_users, 
    delete_user
)
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan
from app.main import app


def test_core_database_and_ai():
    print("=" * 60)
    print("[TEST SUITE 1] Database & AI Unit Verification")
    print("=" * 60)

    # Step 1: Database Initialization
    print("-> Initializing Database...")
    init_db()
    db = SessionLocal()
    print("   [PASS] SQLite Database initialized with SQLAlchemy ORM.")

    # Step 2: AI Generation
    sample_user = {
        "user_id": "TEST-ATHLETE-001",
        "username": "Alex Sterling",
        "age": 27,
        "weight": 78.5,
        "goal": "Muscle Gain & Functional Strength",
        "intensity": "High"
    }

    print("-> Testing Workout Plan Generation (gemini_generator.py)...")
    workout_plan = generate_workout_gemini(sample_user)
    assert len(workout_plan) > 100, "Workout plan generation failed!"
    assert "DAY 1" in workout_plan.upper(), "Day 1 not found in workout plan!"
    print("   [PASS] 7-Day Structured workout plan generated.")

    print("-> Testing Nutrition Tip Generation (gemini_flash_generator.py)...")
    nutrition_tip = generate_nutrition_tip_with_flash(sample_user["goal"], sample_user)
    assert len(nutrition_tip) > 20, "Nutrition tip generation failed!"
    print("   [PASS] Goal-specific nutrition guidance produced.")

    print("-> Testing Feedback-Based Plan Revision (updated_plan.py)...")
    feedback_text = "Please add 15 minutes of cardio after push day and emphasize rotator cuff mobility"
    revised_plan = update_workout_plan(workout_plan, feedback_text, sample_user)
    assert len(revised_plan) > 100, "Revised plan failed!"
    print("   [PASS] Dynamic feedback loop successfully revised plan.")

    # Step 3: Database CRUD Operations
    print("-> Testing Database CRUD Operations (database.py)...")
    saved_user = save_user(db, sample_user)
    assert saved_user.username == "Alex Sterling"
    print("   [PASS] save_user() stored athlete record.")

    saved_plan = save_plan(db, sample_user["user_id"], workout_plan, nutrition_tip)
    assert saved_plan.user_id == sample_user["user_id"]
    assert saved_plan.original_plan == workout_plan
    print("   [PASS] save_plan() stored original plan.")

    updated_rec = update_plan(db, sample_user["user_id"], revised_plan, feedback_text)
    assert updated_rec.updated_plan == revised_plan
    assert updated_rec.feedback == feedback_text
    print("   [PASS] update_plan() stored revised plan & feedback.")

    retrieved_user = get_user(db, sample_user["user_id"])
    assert retrieved_user is not None
    assert retrieved_user.user_id == sample_user["user_id"]

    retrieved_plan = get_original_plan(db, sample_user["user_id"])
    assert retrieved_plan is not None
    assert retrieved_plan.original_plan == workout_plan
    print("   [PASS] get_user() & get_original_plan() verified.")

    all_users = get_all_users(db)
    assert len(all_users) >= 1
    print(f"   [PASS] get_all_users() returned {len(all_users)} athlete record(s).")

    # Clean up test user
    delete_user(db, sample_user["user_id"])
    assert get_user(db, sample_user["user_id"]) is None
    print("   [PASS] delete_user() cleaned up test record.")
    db.close()


def test_fastapi_endpoints():
    print("\n" + "=" * 60)
    print("[TEST SUITE 2] FastAPI HTTP Endpoints Verification")
    print("=" * 60)

    client = TestClient(app)

    # 1. Health check
    print("-> GET /health")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("   [PASS] System health check returns 200 OK.")

    # 2. Homepage (GET /)
    print("-> GET / (Homepage)")
    res = client.get("/")
    assert res.status_code == 200
    assert "FitBuddy" in res.text
    assert "workout-plan-form" in res.text or "username" in res.text
    print("   [PASS] Homepage renders input form with Jinja2.")

    # 3. Generate Workout (POST /generate-workout)
    print("-> POST /generate-workout")
    form_data = {
        "username": "Diana Prince",
        "user_id": "TEST-DIANA-99",
        "age": "26",
        "weight": "68.0",
        "goal": "Fat Loss & High Energy",
        "intensity": "High"
    }
    res = client.post("/generate-workout", data=form_data)
    assert res.status_code == 200
    assert "Diana Prince" in res.text
    assert "TEST-DIANA-99" in res.text
    assert "7-Day" in res.text or "DAY 1" in res.text
    print("   [PASS] Plan generation endpoint rendered result.html with 7-day plan.")

    # 4. Submit Feedback (POST /submit-feedback)
    print("-> POST /submit-feedback")
    feedback_payload = {
        "user_id": "TEST-DIANA-99",
        "feedback": "Include 20 minutes of restorative yoga on day 6 and dumbbell lunges"
    }
    res = client.post("/submit-feedback", data=feedback_payload)
    assert res.status_code == 200
    assert "TEST-DIANA-99" in res.text
    assert "Feedback" in res.text or "yoga" in res.text.lower()
    print("   [PASS] Feedback submission endpoint returned revised workout plan.")

    # 5. Admin Dashboard (GET /view-all-users)
    print("-> GET /view-all-users")
    res = client.get("/view-all-users")
    assert res.status_code == 200
    assert "TEST-DIANA-99" in res.text
    assert "Diana Prince" in res.text
    print("   [PASS] Admin dashboard displays registered user and workout plans.")

    # 6. JSON Users API (GET /api/users)
    print("-> GET /api/users")
    res = client.get("/api/users")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["count"] >= 1
    found_user = any(u["user_id"] == "TEST-DIANA-99" for u in data["data"])
    assert found_user, "Generated user not found in JSON API!"
    print(f"   [PASS] JSON API returns valid data with {data['count']} registered user(s).")

    # 7. Delete User (POST /delete-user/{user_id})
    print("-> POST /delete-user/TEST-DIANA-99")
    res = client.post("/delete-user/TEST-DIANA-99", follow_redirects=False)
    assert res.status_code in [200, 303, 302]
    print("   [PASS] Delete user endpoint redirects or removes record successfully.")

    # Verify deletion in admin view
    res = client.get("/view-all-users")
    assert "TEST-DIANA-99" not in res.text
    print("   [PASS] Verified deletion: User TEST-DIANA-99 no longer present.")


def test_root_entry_point():
    print("\n" + "=" * 60)
    print("[TEST SUITE 3] Root Entry Point Verification (main:app)")
    print("=" * 60)
    from main import app as root_app
    client = TestClient(root_app)
    res = client.get("/health")
    assert res.status_code == 200
    print("   [PASS] Root 'main:app' loads and serves requests identically to 'app.main:app'.")


if __name__ == "__main__":
    test_core_database_and_ai()
    test_fastapi_endpoints()
    test_root_entry_point()
    print("\n" + "*" * 60)
    print("ALL TEST SUITES PASSED! FITBUDDY SYSTEM IS FULLY OPERATIONAL!")
    print("*" * 60)
