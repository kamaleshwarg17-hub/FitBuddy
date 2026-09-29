import os
import logging
import warnings
from typing import Dict, Any

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger(__name__)


def _get_fallback_workout_plan(user_details: Dict[str, Any]) -> str:
    """
    Intelligent fallback plan generation in case Gemini API key is missing or network/quota is unavailable.
    Guarantees the user always receives a personalized 7-day plan matching their inputs.
    """
    name = user_details.get("username", "Athlete")
    goal = user_details.get("goal", "General Fitness").title()
    intensity = user_details.get("intensity", "Medium").title()
    weight = user_details.get("weight", "70")
    age = user_details.get("age", "25")

    sets_reps = {
        "High": "4 sets x 8-12 reps (Heavy resistance, 60s rest)",
        "Medium": "3 sets x 10-15 reps (Moderate resistance, 45s rest)",
        "Low": "2-3 sets x 12-15 reps (Controlled tempo, 60s rest)"
    }.get(intensity, "3 sets x 10-12 reps")

    return f"""================================================================================
7-DAY PERSONALIZED FITNESS BLUEPRINT FOR {name.upper()}
Profile: {age} yrs | Weight: {weight} kg | Goal: {goal} | Intensity: {intensity}
  Model: Local fallback plan [Structured Protocol]
================================================================================

[DAY 1: FOUNDATIONAL PUSH & UPPER STRENGTH]
--------------------------------------------------------------------------------
* Warm-up (8 Mins): Arm circles (20 reps), Cat-Cow stretch (10 reps), 3 mins light jumping jacks or shadow boxing.
* Main Workout:
  1. Barbell / Dumbbell Bench Press — {sets_reps}
  2. Incline Dumbbell Chest Press — {sets_reps}
  3. Overhead Shoulder Press — {sets_reps}
  4. Tricep Rope Cable Pushdowns or Dips — 3 sets x 15 reps
  5. Planks with Shoulder Taps — 3 sets x 45 seconds
* Cooldown & Recovery: Overhead tricep and chest doorway stretch (5 mins). Hydrate with 500ml water and electrolytes.

[DAY 2: LOWER BODY POWER & QUAD FOCUS]
--------------------------------------------------------------------------------
* Warm-up (7 Mins): Leg swings (front & lateral, 15 reps each), Bodyweight squats (20 reps), Glute bridges (15 reps).
* Main Workout:
  1. Barbell Back Squats or Goblet Squats — {sets_reps}
  2. Bulgarian Split Squats — 3 sets x 10 reps each leg
  3. Romanian Deadlifts (RDL) for Hamstrings — {sets_reps}
  4. Standing Calf Raises — 4 sets x 15-20 reps
  5. Hanging Leg Raises or Hollow Body Holds — 3 sets x 12 reps
* Cooldown & Recovery: Foam roll quadriceps and calves; static hamstring stretch for 6 mins.

[DAY 3: AEROBIC CONDITIONING & CORE STABILITY]
--------------------------------------------------------------------------------
* Warm-up (5 Mins): Dynamic thoracic twists and hip openers.
* Main Workout:
  1. Zone 2 Incline Treadmill Walk / Rowing Machine — 25-35 minutes sustained pace
  2. Russian Twists — 3 sets x 20 total reps
  3. Bicycle Crunches — 3 sets x 25 reps
  4. Farmer's Carries — 4 sets x 40-meter walks
* Cooldown & Recovery: Full-body yoga flow (Child's Pose, Cobra, Downward Dog) for 8 mins.

[DAY 4: PULL & POSTERIOR CHAIN DEVELOPMENT]
--------------------------------------------------------------------------------
* Warm-up (7 Mins): Band pull-aparts (25 reps), Dead hangs from pull-up bar (2 x 30s), Scapular retractions.
* Main Workout:
  1. Conventional / Trap-Bar Deadlifts — {sets_reps}
  2. Lat Pulldowns or Pull-ups — {sets_reps}
  3. Bent-Over Barbell Rows — {sets_reps}
  4. Face Pulls for Rear Delts & Posture — 3 sets x 15 reps
  5. Alternating Dumbbell Bicep Curls — 3 sets x 12 reps
* Cooldown & Recovery: Lat stretch on bench, deep breathing for nervous system down-regulation (5 mins).

[DAY 5: FUNCTIONAL HIIT & FULL BODY ATHLETICISM]
--------------------------------------------------------------------------------
* Warm-up (6 Mins): High knees, butt kicks, inchworms into pushups (8 reps).
* Main Workout: Circuit Style (Perform 4 Rounds, 45s work / 15s rest):
  1. Kettlebell Swings — 45 seconds
  2. Push-ups / Plyo Push-ups — 45 seconds
  3. Dumbbell Thrusters (Squat to Overhead Press) — 45 seconds
  4. Mountain Climbers — 45 seconds
  5. Battle Ropes or Shadow Boxing Speed Drill — 45 seconds
* Cooldown & Recovery: Pigeon stretch for hips and lower back decompression (6 mins).

[DAY 6: ACTIVE RECOVERY & MOBILITY RESTORATION]
--------------------------------------------------------------------------------
* Activity: Low-intensity 45-minute outdoor nature walk, gentle swimming, or guided mobility session.
* Mobility Routine: Focus on hip internal/external rotation, thoracic spine extension, and ankle dorsiflexion.
* Tip: Prioritize deep sleep (8+ hours) and prepare healthy whole-food meals for the upcoming week.

[DAY 7: TOTAL REST & METABOLIC RESET]
--------------------------------------------------------------------------------
* Rest Protocol: Complete physical rest. Allow central nervous system and muscular tissue to repair and rebuild.
* Self-Care: Optional light sauna, contrast shower, or epsom salt warm bath.
* Nutrition Focus: Maintain protein intake to preserve lean muscle tissue and replenish glycogen stores.

================================================================================
COACH'S PROGRESSION NOTE:
Log weights, reps, and perceived exertion (RPE). Aim to progressively overload by 2-5% every 2 weeks.
================================================================================
"""


def generate_workout_gemini(user_details: Dict[str, Any]) -> str:
    """
    Generates a structured 7-day personalized workout plan using Google Gemini.
    Falls back reliably if API is not configured or temporary network issue occurs.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    name = user_details.get("username", "User")
    age = user_details.get("age", "25")
    weight = user_details.get("weight", "70")
    goal = user_details.get("goal", "General Fitness")
    intensity = user_details.get("intensity", "Medium")

    prompt = f"""
You are FitBuddy's master strength and conditioning coach. Generate a high-performance, personalized 7-Day Workout Plan tailored to the user profile below.

User Profile:
- Name: {name}
- Age: {age} years
- Weight: {weight} kg
- Fitness Goal: {goal}
- Target Intensity: {intensity}

Requirements:
1. Provide a comprehensive Day 1 to Day 7 structured workout schedule.
2. For EVERY day include:
   - Day title & primary muscle focus
   - Warm-up routine (5-10 minutes with specific dynamic movements)
   - Main workout routine (List each exercise, target sets, target reps, and rest intervals)
   - Cooldown & recovery guidance (stretches, breathing, hydration)
3. Tailor the exercise selection, volume, and rest periods strictly to their goal ({goal}) and intensity ({intensity}).
4. Ensure at least 1-2 days include active recovery or strategic rest.
5. Format the output clearly with clean sections and headers suitable for display in text or code blocks.
"""

    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning("Gemini workout generation failed; using fallback: %s", e)

    # Return structured fallback plan if API is unconfigured or failed
    return _get_fallback_workout_plan(user_details)
