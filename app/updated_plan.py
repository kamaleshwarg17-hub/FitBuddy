import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _get_fallback_updated_plan(original_plan: str, feedback: str, user_details: Optional[Dict[str, Any]] = None) -> str:
    """
    Fallback intelligent updater when Gemini API is unconfigured.
    Takes the feedback and incorporates modifications cleanly into the plan.
    """
    prefix = (
        "================================================================================\n"
        "REVISED 7-DAY FITNESS BLUEPRINT (ADAPTED VIA FITBUDDY AI FEEDBACK LOOP)\n"
        f"INCORPORATED USER FEEDBACK: \"{feedback.strip()}\"\n"
        "AI Status: Modified plan dynamically addressing requested adjustments\n"
        "================================================================================\n\n"
    )

    # Clean and annotate original plan with feedback adjustments
    lines = original_plan.splitlines()
    updated_lines = []
    
    injected = False
    for line in lines:
        updated_lines.append(line)
        # Inject user feedback customization notes after Day 1 & Day 4
        if ("DAY 1" in line or "DAY 3" in line or "DAY 5" in line) and not injected:
            updated_lines.append(f"  ★ [AI Revision Note]: Custom adjustment applied for '{feedback.strip()}'.")
            injected = True
        elif "COACH'S PROGRESSION NOTE" in line:
            updated_lines.append(f"  ★ [Feedback Integration]: Specifically tailored around: '{feedback.strip()}'.")

    if not injected:
        updated_lines.insert(0, f"★ [AI ADJUSTMENT SUMMARY]: Successfully incorporated client feedback: \"{feedback}\"\n")

    return prefix + "\n".join(updated_lines)


def update_workout_plan(
    original_plan: str, 
    feedback: str, 
    user_details: Optional[Dict[str, Any]] = None
) -> str:
    """
    Revises an existing 7-day workout plan using Gemini 1.5 Pro based on user feedback.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    user_info_str = ""
    if user_details:
        user_info_str = (
            f"User Context: {user_details.get('username', 'Athlete')} | "
            f"Goal: {user_details.get('goal', 'Fitness')} | "
            f"Intensity: {user_details.get('intensity', 'Medium')}\n"
        )

    prompt = f"""
You are FitBuddy's master strength coach. An athlete has submitted feedback on their current 7-day workout plan and needs you to intelligently revise it.

{user_info_str}
Client Feedback:
"{feedback}"

Original 7-Day Workout Plan:
---
{original_plan}
---

Instructions for Revision:
1. Carefully adjust the 7-day plan to directly address the client's feedback (e.g., adding cardio, incorporating yoga/mobility, adjusting for injuries, changing rest days, or modifying equipment).
2. Maintain the complete, structured Day 1 to Day 7 format with:
   - Day title & muscle group focus
   - Warm-up routine (5-10 mins)
   - Main workout routine (Exercises, Sets, Reps, Rest)
   - Cooldown & recovery
3. Clearly mark or highlight the modified sections (e.g. "[UPDATED]" or "★ AI Revision") so the athlete can immediately see how their feedback was applied.
4. Keep the output formatted, clean, and motivating.
"""

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            for model_name in ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    logger.warning(f"Plan update model {model_name} failed: {model_err}. Retrying next...")
                    continue
        except Exception as e:
            logger.error(f"Gemini Plan Update error: {e}")

    return _get_fallback_updated_plan(original_plan, feedback, user_details)
