from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

import json
from datetime import datetime
from collections import defaultdict


# -------------------------
# Utilidades
# -------------------------

def _group_by_class(data):
    grouped = defaultdict(list)
    for entry in data:
        method = entry["method"]
        key = f"{method.get('file_path', '')}::{method.get('class_name', '')}"
        grouped[key].append(entry)
    return grouped


def _clean(text):
    if not text:
        return ""
    return str(text)


# -------------------------
# Generador principal
# -------------------------

def generate_pdf(input_path="reports/output.json", output_path="reports/output.pdf"):
    with open(input_path) as f:
        data = json.load(f)

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    # estilos adicionales
    styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=8))
    styles.add(ParagraphStyle(name="SectionTitle", fontSize=12, spaceAfter=6, spaceBefore=6))

    content = []

    # -------------------------
    # PORTADA
    # -------------------------
    content.append(Paragraph("<b>AutoDoc Documentation Manual</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Generated: {datetime.utcnow().isoformat()}", styles["Normal"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Sistema: AutoDoc", styles["Normal"]))
    content.append(PageBreak())

    # -------------------------
    # ÍNDICE
    # -------------------------
    content.append(Paragraph("<b>Índice</b>", styles["Heading1"]))

    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontSize=10, name="TOCHeading1", leftIndent=20),
        ParagraphStyle(fontSize=9, name="TOCHeading2", leftIndent=40),
    ]

    content.append(toc)
    content.append(PageBreak())

    # -------------------------
    # RESUMEN EJECUTIVO
    # -------------------------
    content.append(Paragraph("<b>Resumen Ejecutivo</b>", styles["Heading1"]))
    content.append(Paragraph(
        "Este documento presenta la documentación generada automáticamente a partir del análisis "
        "de código fuente Java mediante el sistema AutoDoc. El objetivo es proporcionar una visión "
        "estructurada y completa del comportamiento de los métodos analizados.",
        styles["BodyText"]
    ))
    content.append(PageBreak())

    # -------------------------
    # AGRUPACIÓN POR CLASE
    # -------------------------
    grouped = _group_by_class(data)

    for class_key, methods in grouped.items():

        file_path, class_name = class_key.split("::")

        # -------------------------
        # Clase
        # -------------------------
        content.append(Paragraph(f"<b>Clase: {class_name}</b>", styles["Heading1"]))
        content.append(Paragraph(f"Archivo: {file_path}", styles["Normal"]))
        content.append(Spacer(1, 12))

        for entry in methods:
            method = entry["method"]
            jd = method.get("javadoc", {})

            # -------------------------
            # Firma
            # -------------------------
            content.append(Paragraph(
                f"<b>{method['signature']}</b>",
                styles["Heading2"]
            ))

            # -------------------------
            # Descripción
            # -------------------------
            desc = jd.get("purpose") or jd.get("description")
            if desc:
                content.append(Paragraph("<b>Descripción:</b>", styles["SectionTitle"]))
                content.append(Paragraph(_clean(desc), styles["BodyText"]))

            # -------------------------
            # Parámetros
            # -------------------------
            if jd.get("params"):
                content.append(Paragraph("<b>Parámetros:</b>", styles["SectionTitle"]))
                for p in jd["params"]:
                    content.append(Paragraph(f"{p['name']}: {p['description']}", styles["BodyText"]))

            # -------------------------
            # Return
            # -------------------------
            if jd.get("return"):
                content.append(Paragraph("<b>Salida:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["return"], styles["BodyText"]))

            # -------------------------
            # Ejemplo
            # -------------------------
            if jd.get("example"):
                content.append(Paragraph("<b>Ejemplo de uso:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["example"], styles["CodeBlock"]))

            # -------------------------
            # Métodos usados
            # -------------------------
            if jd.get("uses"):
                content.append(Paragraph("<b>Métodos utilizados:</b>", styles["SectionTitle"]))
                for u in jd["uses"]:
                    content.append(Paragraph(u, styles["BodyText"]))

            # -------------------------
            # Pre/Post
            # -------------------------
            if jd.get("precondition"):
                content.append(Paragraph("<b>Precondiciones:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["precondition"], styles["BodyText"]))

            if jd.get("postcondition"):
                content.append(Paragraph("<b>Postcondiciones:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["postcondition"], styles["BodyText"]))

            # -------------------------
            # Side effects
            # -------------------------
            if jd.get("sideEffects"):
                content.append(Paragraph("<b>Efectos secundarios:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["sideEffects"], styles["BodyText"]))

            # -------------------------
            # Requirements
            # -------------------------
            if jd.get("requirements"):
                content.append(Paragraph("<b>Requisitos:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["requirements"], styles["BodyText"]))

            # -------------------------
            # Exceptions
            # -------------------------
            if jd.get("throws"):
                content.append(Paragraph("<b>Excepciones:</b>", styles["SectionTitle"]))
                for t in jd["throws"]:
                    content.append(Paragraph(t, styles["BodyText"]))

            # -------------------------
            # Business rules / ticket
            # -------------------------
            if jd.get("businessRule"):
                content.append(Paragraph("<b>Reglas de negocio:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["businessRule"], styles["BodyText"]))

            if jd.get("ticket"):
                content.append(Paragraph("<b>Trazabilidad:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["ticket"], styles["BodyText"]))

            # -------------------------
            # Notas
            # -------------------------
            if jd.get("notes"):
                content.append(Paragraph("<b>Notas:</b>", styles["SectionTitle"]))
                content.append(Paragraph(jd["notes"], styles["BodyText"]))

            # -------------------------
            # Metadata
            # -------------------------
            if jd.get("since"):
                content.append(Paragraph(f"<b>Since:</b> {jd['since']}", styles["BodyText"]))

            if jd.get("deprecated"):
                content.append(Paragraph(f"<b>Deprecated:</b> {jd['deprecated']}", styles["BodyText"]))

            if jd.get("author"):
                content.append(Paragraph(f"<b>Autor:</b> {jd['author']}", styles["BodyText"]))

            content.append(Spacer(1, 16))

        content.append(PageBreak())

    doc.build(content)