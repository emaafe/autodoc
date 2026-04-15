from __future__ import annotations
import json
import os


def generate_html(input_path="reports/output.json", output_path="docs/index.html"):
    with open(input_path) as f:
        data = json.load(f)

    os.makedirs("docs", exist_ok=True)

    html = """
    <html>
    <head>
        <title>AutoDoc Documentation</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; }
            .method { margin-bottom: 30px; }
            .section { margin-left: 20px; }
            code { background: #f4f4f4; padding: 5px; display: block; }
        </style>
    </head>
    <body>
    """

    html += "<h1>AutoDoc Documentation</h1>"

    for entry in data:
        method = entry["method"]
        jd = method.get("javadoc", {})

        html += "<div class='method'>"
        html += f"<h2>{method['signature']}</h2>"

        desc = jd.get("purpose") or jd.get("description")
        if desc:
            html += f"<div class='section'><b>Descripción:</b> {desc}</div>"

        if jd.get("params"):
            html += "<div class='section'><b>Parámetros:</b><ul>"
            for p in jd["params"]:
                html += f"<li>{p['name']}: {p['description']}</li>"
            html += "</ul></div>"

        if jd.get("return"):
            html += f"<div class='section'><b>Salida:</b> {jd['return']}</div>"

        if jd.get("example"):
            html += "<div class='section'><b>Ejemplo:</b>"
            html += f"<code>{jd['example']}</code></div>"

        if jd.get("notes"):
            html += f"<div class='section'><b>Notas:</b> {jd['notes']}</div>"

        html += "</div>"

    html += "</body></html>"

    with open(output_path, "w") as f:
        f.write(html)