from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


# -------------------------
# Parámetro documentado
# -------------------------
@dataclass
class ParameterDoc:
    name: str
    description: str


# -------------------------
# Información de Javadoc
# -------------------------
@dataclass
class JavadocInfo:
    exists: bool
    description: str
    params: list[ParameterDoc] = field(default_factory=list)
    return_value: str = ""

    # 👉 NUEVO: tags extendidos
    extra_tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base = {
            "exists": self.exists,
            "description": self.description,
            "params": [asdict(param) for param in self.params],
            "return": self.return_value,
        }

        # agregar dinámicamente tags extra
        for k, v in self.extra_tags.items():
            base[k] = v

        return base


# -------------------------
# Parámetro de método
# -------------------------
@dataclass
class MethodParameter:
    name: str
    type: str


# -------------------------
# Método extraído
# -------------------------
@dataclass
class ExtractedMethod:
    file_path: str
    class_name: str
    method_name: str
    signature: str
    parameters: list[MethodParameter]
    return_type: str
    javadoc: JavadocInfo
    method_body: str
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "signature": self.signature,
            "parameters": [asdict(param) for param in self.parameters],
            "return_type": self.return_type,
            "javadoc": self.javadoc.to_dict(),
            "method_body": self.method_body,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }