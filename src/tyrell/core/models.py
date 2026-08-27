"""Modelos de datos para la generación sintética en TYRELL."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DatasetRule(BaseModel):
    name: str
    type: str  # "integer", "float", "string", "array", "boundary"
    min_val: Optional[int] = None
    max_val: Optional[int] = None
    length: Optional[int] = 10
    include_extremes: bool = True
    charset: Optional[str] = None


class DatasetSpec(BaseModel):
    name: str = "suite"
    count: int = 10
    seed: int = 42
    format_template: str = "{input}"
    rules: List[DatasetRule] = Field(default_factory=list)


class GeneratedTestCase(BaseModel):
    index: int
    input_content: str
    output_content: Optional[str] = None
    in_filename: str
    out_filename: Optional[str] = None
