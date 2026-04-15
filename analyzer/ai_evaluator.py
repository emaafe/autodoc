from __future__ import annotations

import os
from typing import Any

import google.generativeai as genai

from analyzer.prompt_builder import build_prompt


# Configuración
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def evaluate_with_ai(method: dict[str, Any]) -> dict[str, Any]:
    prompt = build_prompt(method)

    try:
        response = model.generate_content(prompt)

        text = response.text.strip()

        return _parse_response(text)

    except Exception as e:
        return {
            "result": "UNCERTAIN",
            "explanation": f"Error al consultar IA: {str(e)}"
        }


# -------------------------
# Parseo de respuesta
# -------------------------

def _parse_response(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("CONSISTENT"):
        return {
            "result": "CONSISTENT",
            "explanation": ""
        }

    if text.startswith("INCONSISTENT"):
        explanation = text.replace("INCONSISTENT:", "").strip()
        return {
            "result": "INCONSISTENT",
            "explanation": explanation
        }

    if text.startswith("UNCERTAIN"):
        explanation = text.replace("UNCERTAIN:", "").strip()
        return {
            "result": "UNCERTAIN",
            "explanation": explanation
        }

    # fallback
    return {
        "result": "UNCERTAIN",
        "explanation": f"Respuesta inesperada: {text}"
    }