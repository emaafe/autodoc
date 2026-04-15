from __future__ import annotations

import re
from pathlib import Path

import javalang

from analyzer.models import ExtractedMethod, JavadocInfo, MethodParameter, ParameterDoc


_METHOD_MODIFIERS = {
    "public",
    "private",
    "protected",
    "static",
    "final",
    "abstract",
    "synchronized",
    "native",
    "strictfp",
    "default",
}


def extract_methods_from_file(file_path: str) -> list[ExtractedMethod]:
    """
    Extract analyzable methods from a Java file.

    Current rules:
    - include methods with body
    - exclude constructors
    - exclude interface methods without body
    - include public/private/protected methods
    """
    source = Path(file_path).read_text(encoding="utf-8")
    return extract_methods_from_source(source=source, file_path=file_path)


def extract_methods_from_source(source: str, file_path: str = "<memory>") -> list[ExtractedMethod]:
    tree = javalang.parse.parse(source)

    lines = source.splitlines()
    methods: list[ExtractedMethod] = []

    for class_decl in tree.types:
        if not isinstance(class_decl, (javalang.tree.ClassDeclaration, javalang.tree.EnumDeclaration)):
            continue

        class_name = class_decl.name

        for method in class_decl.methods:
            if not _is_analyzable_method(method):
                continue

            method_line = method.position.line if method.position else 1
            line_start = _find_method_start_line(lines, method_line)
            line_end = _find_method_end_line(lines, line_start)
            method_body = _extract_block_from_lines(lines, line_start, line_end)

            javadoc_raw = _extract_javadoc_before_line(lines, line_start)
            javadoc_info = parse_javadoc(javadoc_raw)

            parameters = [
                MethodParameter(
                    name=param.name,
                    type=_type_to_string(param.type),
                )
                for param in method.parameters
            ]

            return_type = _type_to_string(method.return_type) if method.return_type else "void"

            extracted = ExtractedMethod(
                file_path=file_path,
                class_name=class_name,
                method_name=method.name,
                signature=_build_signature(method, return_type),
                parameters=parameters,
                return_type=return_type,
                javadoc=javadoc_info,
                method_body=method_body,
                line_start=line_start,
                line_end=line_end,
            )
            methods.append(extracted)

    return methods

def parse_javadoc(raw_javadoc: str | None) -> JavadocInfo:
    if not raw_javadoc:
        return JavadocInfo(
            exists=False,
            description="",
            params=[],
            return_value=""
        )

    lines = _clean_javadoc_lines(raw_javadoc)

    description_lines = []
    params = []
    return_value = ""

    # NUEVO: diccionario de tags
    tags = {
        "purpose": "",
        "inputs": "",
        "outputs": "",
        "example": "",
        "uses": [],
        "precondition": "",
        "postcondition": "",
        "sideEffects": "",
        "businessRule": "",
        "ticket": "",
        "requirements": "",
        "notes": "",
        "since": "",
        "deprecated": "",
        "author": "",
        "throws": []
    }

    current_tag = None
    current_buffer = []
    current_param_name = None

    def flush():
        nonlocal current_tag, current_buffer, current_param_name, return_value

        text = " ".join(current_buffer).strip()

        if not text:
            current_tag = None
            current_buffer = []
            return

        if current_tag == "param" and current_param_name:
            params.append(ParameterDoc(name=current_param_name, description=text))

        elif current_tag == "return":
            return_value = text

        elif current_tag == "throws":
            tags["throws"].append(text)

        elif current_tag in tags:
            if isinstance(tags[current_tag], list):
                tags[current_tag].append(text)
            else:
                tags[current_tag] = text

        elif current_tag is None:
            description_lines.append(text)

        current_tag = None
        current_buffer = []
        current_param_name = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("@param"):
            flush()
            match = re.match(r"@param\s+(\w+)\s*(.*)", line)
            current_tag = "param"
            current_param_name = match.group(1) if match else None
            current_buffer = [match.group(2)] if match and match.group(2) else []
            continue

        if line.startswith("@return"):
            flush()
            current_tag = "return"
            current_buffer = [line.replace("@return", "").strip()]
            continue

        if line.startswith("@throws"):
            flush()
            current_tag = "throws"
            current_buffer = [line.replace("@throws", "").strip()]
            continue

        # TAGS PERSONALIZADOS
        match = re.match(r"@(\w+)\s*(.*)", line)
        if match:
            flush()
            tag_name = match.group(1)
            content = match.group(2)

            current_tag = tag_name
            current_buffer = [content] if content else []
            continue

        # CONTENIDO CONTINUADO
        current_buffer.append(line)

    flush()

    description = " ".join(description_lines).strip()

    jd = JavadocInfo(
        exists=True,
        description=description,
        params=params,
        return_value=return_value
    )

    # 👉 adjuntamos tags extra dinámicamente
    jd.extra_tags = tags

    return jd

def _is_analyzable_method(method: javalang.tree.MethodDeclaration) -> bool:
    # Exclude methods without body (e.g. abstract/interface declarations without implementation)
    if method.body is None:
        return False

    return True


def _find_method_start_line(lines: list[str], method_line: int) -> int:
    """
    Expand upward to include annotations immediately above the method signature.
    """
    index = max(method_line - 1, 0)

    while index > 0:
        previous = lines[index - 1].strip()
        if previous.startswith("@"):
            index -= 1
            continue
        break

    return index + 1


def _find_method_end_line(lines: list[str], start_line: int) -> int:
    """
    Finds the end of the method block by tracking braces from the method start.
    """
    brace_count = 0
    started = False

    for idx in range(start_line - 1, len(lines)):
        line = lines[idx]

        for char in line:
            if char == "{":
                brace_count += 1
                started = True
            elif char == "}":
                brace_count -= 1

        if started and brace_count == 0:
            return idx + 1

    return len(lines)


def _extract_block_from_lines(lines: list[str], start_line: int, end_line: int) -> str:
    return "\n".join(lines[start_line - 1 : end_line])


def _extract_javadoc_before_line(lines: list[str], start_line: int) -> str | None:
    """
    Extract the Javadoc block immediately preceding the method, ignoring annotations
    and blank lines between the Javadoc and the method.
    """
    idx = start_line - 2

    while idx >= 0 and not lines[idx].strip():
        idx -= 1

    while idx >= 0 and lines[idx].strip().startswith("@"):
        idx -= 1

    if idx < 0 or "*/" not in lines[idx]:
        return None

    end_idx = idx

    while idx >= 0 and "/**" not in lines[idx]:
        idx -= 1

    if idx < 0:
        return None

    start_idx = idx
    return "\n".join(lines[start_idx : end_idx + 1])


def _clean_javadoc_lines(raw_javadoc: str) -> list[str]:
    content = raw_javadoc.strip()

    if content.startswith("/**"):
        content = content[3:]
    if content.endswith("*/"):
        content = content[:-2]

    result: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("*"):
            stripped = stripped[1:].lstrip()
        result.append(stripped)

    return result


def _type_to_string(type_node: object | None) -> str:
    if type_node is None:
        return "void"

    if isinstance(type_node, str):
        return type_node

    name = getattr(type_node, "name", None)
    if not name:
        return str(type_node)

    dimensions = getattr(type_node, "dimensions", None) or []
    suffix = "[]" * len(dimensions)

    arguments = getattr(type_node, "arguments", None)
    if arguments:
        parts = []
        for arg in arguments:
            arg_type = getattr(arg, "type", None)
            if arg_type is not None:
                parts.append(_type_to_string(arg_type))
            else:
                parts.append(str(arg))
        return f"{name}<{', '.join(parts)}>{suffix}"

    return f"{name}{suffix}"


def _build_signature(method: javalang.tree.MethodDeclaration, return_type: str) -> str:
    modifiers = sorted(method.modifiers.intersection(_METHOD_MODIFIERS))
    modifiers_part = " ".join(modifiers)

    params = []
    for param in method.parameters:
        param_type = _type_to_string(param.type)
        if getattr(param, "varargs", False):
            param_type = f"{param_type}..."
        params.append(f"{param_type} {param.name}")

    signature_parts = []
    if modifiers_part:
        signature_parts.append(modifiers_part)
    signature_parts.append(return_type)
    signature_parts.append(f"{method.name}({', '.join(params)})")

    return " ".join(signature_parts)