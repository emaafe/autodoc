from analyzer.changed_files import get_analyzable_files
from analyzer.java_extractor import extract_methods_from_file
from analyzer.normalizer import normalize_methods
from analyzer.rules import evaluate_method
from analyzer.ai_evaluator import evaluate_with_ai
from analyzer.decision_engine import decide
from analyzer.pr_commenter import post_comment
from analyzer.report_generator import generate_pdf
from analyzer.html_generator import generate_html

import json
import os


def main():
    files = get_analyzable_files()
    all_results = []

    for file in files:
        extracted = extract_methods_from_file(file)
        normalized = normalize_methods(extracted)

        for method in normalized:
            rules_eval = evaluate_method(method)

            # Ejecutar IA solo si corresponde
            if rules_eval["status"] != "FAIL" and not rules_eval.get("exempted", False):
                ai_eval = evaluate_with_ai(method)
            else:
                ai_eval = None

            final = decide(rules_eval, ai_eval)

            all_results.append({
                "file": file,
                "method": method["method_name"],
                "final_status": final["final_status"],
                "details": final
            })

    # Crear carpeta de reportes
    os.makedirs("reports", exist_ok=True)

    # Guardar JSON
    with open("reports/output.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("=== AutoDoc Results ===")
    print(json.dumps(all_results, indent=2))

    # Publicar comentario en PR
    post_comment()

    # Generar PDF
    generate_pdf()

    #Generar HTML
    generate_html()

if __name__ == "__main__":
    main()