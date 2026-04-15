from __future__ import annotations

from typing import Any


def decide(rules_eval: dict[str, Any], ai_eval: dict[str, Any] | None) -> dict[str, Any]:
    """
    Combina reglas + IA para producir decisión final.
    """

    # -------------------------
    # Caso 1: fallo de reglas
    # -------------------------
    if rules_eval["status"] == "FAIL":
        return {
            "final_status": "FAIL",
            "reason": "Reglas no cumplidas",
            "details": rules_eval
        }

    # -------------------------
    # Caso 2: método exento
    # -------------------------
    if rules_eval.get("exempted", False):
        return {
            "final_status": "PASS",
            "reason": "Método exento por policy",
            "details": rules_eval
        }

    # -------------------------
    # Caso 3: sin IA (fallback)
    # -------------------------
    if ai_eval is None:
        return {
            "final_status": "NEEDS REVIEW",
            "reason": "Sin evaluación IA",
            "details": rules_eval
        }

    ai_result = ai_eval["result"]

    # -------------------------
    # Caso 4: IA consistente
    # -------------------------
    if ai_result == "CONSISTENT":
        return {
            "final_status": "PASS",
            "reason": "Consistente según IA",
            "details": ai_eval
        }

    # -------------------------
    # Caso 5: IA inconsistente
    # -------------------------
    if ai_result == "INCONSISTENT":
        return {
            "final_status": "NEEDS REVIEW",
            "reason": ai_eval.get("explanation", ""),
            "details": ai_eval
        }

    # -------------------------
    # Caso 6: IA incierta
    # -------------------------
    if ai_result == "UNCERTAIN":
        return {
            "final_status": "NEEDS REVIEW",
            "reason": ai_eval.get("explanation", ""),
            "details": ai_eval
        }

    # -------------------------
    # fallback
    # -------------------------
    return {
        "final_status": "NEEDS REVIEW",
        "reason": "Resultado IA desconocido",
        "details": ai_eval
    }