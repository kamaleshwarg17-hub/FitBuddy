import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _get_fallback_nutrition_tip(goal: str, user_details: Optional[Dict[str, Any]] = None) -> str:
    """
    Returns curated, high-impact nutrition and recovery guidance based on goal.
    Used when Gemini Flash API key is missing or offline.
    """
    g = goal.lower()
    if "muscle" in g or "bulk" in g or "strength" in g:
        return (
            "⚡ Post-Workout Anabolic Window & Protein Synthesis:\n"
            "Aim for 1.6 to 2.2 grams of high-quality protein per kilogram of body weight daily. "
            "Within 45-60 minutes after your strength session, consume 25-35g of rapid-digesting protein "
            "(whey isolate, eggs, or Greek yogurt) paired with complex carbohydrates (oatmeal, bananas, or sweet potatoes) "
            "to maximize muscle protein synthesis and replenish depleted intramuscular glycogen stores."
        )
    elif "loss" in g or "fat" in g or "lean" in g:
        return (
            "🔥 Satiety Optimization & Caloric Deficit Hydration:\n"
            "Maintain a steady moderate caloric deficit (300-500 kcal below maintenance) while elevating your protein "
            "intake (1.8g - 2.2g per kg) to protect lean muscle mass. Consume 500ml of cold water 20 minutes before each meal "
            "and load half your plate with fiber-dense cruciferous greens (spinach, broccoli, zucchini) to blunt hunger hormones "
            "and stabilize blood glucose spikes."
        )
    elif "endurance" in g or "running" in g or "cardio" in g:
        return (
            "💧 Glycogen Replenishment & Electrolyte Balance:\n"
            "For sustained aerobic output, prioritize complex carbohydrate timing 2-3 hours pre-workout (quinoa, brown rice, bananas). "
            "During sessions lasting longer than 60 minutes, supplement with essential electrolytes (sodium, potassium, magnesium) "
            "to prevent muscular cramping and preserve neuromuscular power output."
        )
    elif "flex" in g or "mobility" in g or "yoga" in g:
        return (
            "🌱 Collagen Synthesis & Anti-Inflammatory Recovery:\n"
            "Incorporate collagen peptides paired with Vitamin C (such as citrus fruits or berries) 45 minutes prior to mobility work "
            "to stimulate tendon and ligament remodeling. Incorporate omega-3 rich fatty acids (wild salmon, chia seeds, walnuts) "
            "to reduce systemic joint inflammation."
        )
    else:
        return (
            "🥑 Balanced Micronutrient Density & Sleep Quality:\n"
            "Base 80% of your nutrition on single-ingredient, unprocessed whole foods: lean proteins, colorful vegetables, healthy fats "
            "(avocados, extra virgin olive oil), and slow-burning carbohydrates. Ensure your last meal is consumed 2-3 hours before bed, "
            "and hydrate consistently with at least 3 liters of filtered water daily."
        )


def generate_nutrition_tip_with_flash(goal: str, user_details: Optional[Dict[str, Any]] = None) -> str:
    """
    Generates a concise, practical nutrition and recovery tip tailored to the user's goal using Gemini Flash.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    prompt = f"""
You are FitBuddy's sports nutritionist. Provide a concise, highly practical, and scientifically sound nutrition and recovery tip specifically tailored for a client with the goal: "{goal}".

Guidelines:
- Length: 2-4 sentences or a punchy bulleted tip.
- Address optimal nutrient timing, protein/carb prioritization, hydration, or recovery techniques.
- Highlight specific foods (e.g. chicken, salmon, Greek yogurt, oats, chia seeds, leafy greens).
- Tone: Motivating, actionable, professional.
"""

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Prefer Gemini 1.5 Flash for speed & efficiency
            for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    logger.warning(f"Flash model {model_name} failed: {model_err}. Trying next...")
                    continue
        except Exception as e:
            logger.error(f"Gemini Flash API error: {e}")

    return _get_fallback_nutrition_tip(goal, user_details)
