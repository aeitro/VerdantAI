import requests
import json
import re

OPENROUTER_API_KEY = "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"

# ── Model fallback chain — all free tier ──────────────────────────────────────
MODELS = [
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-4b-it:free",
]

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "PlantAI",
}

# ── In-memory cache — persists for the lifetime of the backend process ────────
_cache: dict[str, dict] = {}


def clean_label(raw: str) -> str:
    """Apple___Apple_scab → Apple scab on Apple"""
    parts = raw.split("___")
    if len(parts) == 2:
        plant, condition = parts
        plant = plant.replace("_", " ").replace(",", "").strip()
        condition = condition.replace("_", " ").strip()
        return f"{condition} on {plant}"
    return raw.replace("_", " ")


def build_prompt(disease_label: str) -> str:
    return f"""You are a plant pathology expert. A plant leaf has been diagnosed with: "{disease_label}".

Return ONLY a valid JSON object with exactly these keys and limits:

{{
  "overview": "2 sentences max. What the disease is and how it spreads.",
  "severity": "Low | Medium | High",
  "remedies": ["max 3 items, each under 12 words, actionable treatments"],
  "dietary_tips": ["max 3 items, each under 12 words, soil/nutrient/watering tips"],
  "lifestyle_steps": ["max 3 items, each under 12 words, prevention and care habits"],
  "when_to_see_expert": "1 sentence. Clear trigger condition for consulting an agronomist."
}}

Rules:
- Every list item must be a short, actionable phrase
- No bullet points, no markdown, no numbering inside strings
- No extra text outside the JSON object
- Severity must be exactly one of: Low, Medium, High"""


def call_model(model: str, prompt: str) -> dict:
    """
    Call a single model. Returns parsed dict on success.
    Raises requests.HTTPError on 429 / server error.
    Raises ValueError if JSON parsing fails.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)


def get_remedy(predicted_class: str) -> dict:
    """
    Try each model in MODELS in order.
    Returns remedy dict, or an error dict if all models fail.
    """
    disease_label = clean_label(predicted_class)

    if predicted_class in _cache:
        return _cache[predicted_class]

    prompt = build_prompt(disease_label)
    last_error = ""

    for model in MODELS:
        try:
            result = call_model(model, prompt)
            _cache[predicted_class] = result
            return result

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == 0:
                last_error = f"Model {model} got no response (connection dropped)"
            elif status == 429:
                last_error = f"Model {model} rate limited (429)"
            else:
                last_error = f"Model {model} HTTP error: {status}"
            continue

        except requests.exceptions.Timeout:
            last_error = f"Model {model} timed out"
            continue

        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to OpenRouter API."}

        except (json.JSONDecodeError, KeyError, ValueError):
            last_error = f"Model {model} returned invalid JSON"
            continue

        except Exception as e:
            last_error = f"Model {model} unexpected error: {str(e)}"
            continue

    return {"error": f"All models failed. Last error: {last_error}"}