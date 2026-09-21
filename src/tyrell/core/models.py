"""Modelos de datos para la generación sintética en TYRELL."""

import string
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

# Tipos que el motor sabe generar. Antes `type` era un `str` libre: un typo como
# `intger` caía en silencio a `randint(1, 100)` y el docente creía tener otro dato.
TipoDato = Literal["integer", "float", "string", "array"]


class DatasetRule(BaseModel):
    # `forbid`: una clave desconocida (p. ej. `max_value` en vez de `max_val`) se
    # ignoraba sin aviso y la regla quedaba con sus valores por defecto.
    model_config = ConfigDict(extra="forbid")

    name: str
    type: TipoDato
    min_val: Optional[int] = None
    max_val: Optional[int] = None
    length: Optional[int] = 10
    include_extremes: bool = True
    charset: Optional[str] = None


class DatasetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "suite"
    count: int = Field(10, ge=1)
    seed: int = 42
    format_template: str = "{input}"
    rules: List[DatasetRule] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validar_plantilla(self) -> "DatasetSpec":
        """La plantilla debe usar exactamente los nombres de las reglas.

        Con una plantilla sin placeholders (por ejemplo `"%d %d"` en estilo
        printf) todos los `.in` salían idénticos y con el texto literal; un
        placeholder sin regla terminaba en un KeyError sin contexto.
        """
        if not self.rules:
            return self

        usados = {campo for _, campo, _, _ in string.Formatter().parse(self.format_template) if campo}
        nombres = [r.name for r in self.rules]

        if not usados:
            raise ValueError(
                "format_template no usa ningún placeholder: todos los casos serían idénticos. "
                "Escribí los campos entre llaves, p. ej. \"{" + nombres[0] + "}\"."
            )
        desconocidos = sorted(usados - set(nombres))
        if desconocidos:
            raise ValueError(
                f"format_template usa placeholders sin regla: {desconocidos}. Reglas definidas: {nombres}."
            )
        sin_usar = [n for n in nombres if n not in usados]
        if sin_usar:
            raise ValueError(
                f"Las reglas {sin_usar} no aparecen en format_template, así que no afectan a ningún caso."
            )
        return self


class GeneratedTestCase(BaseModel):
    index: int
    input_content: str
    output_content: Optional[str] = None
    in_filename: str
    out_filename: Optional[str] = None
    advertencia: Optional[str] = None
