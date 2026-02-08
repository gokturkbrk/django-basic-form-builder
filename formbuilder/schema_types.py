from __future__ import annotations

from typing import Literal, TypedDict


class TextFieldConfig(TypedDict, total=False):
    minLength: int
    maxLength: int
    pattern: str
    inputMode: str
    prefix: str
    suffix: str


class NumberFieldConfig(TypedDict, total=False):
    min: float
    max: float
    step: float
    prefix: str
    suffix: str
    unit: str


class TextareaFieldConfig(TypedDict, total=False):
    rows: int
    minLength: int
    maxLength: int
    autoResize: bool


class DropdownOption(TypedDict):
    value: str
    label: str


class DropdownFieldConfig(TypedDict, total=False):
    options: list[DropdownOption]
    allowMultiple: bool
    allowOther: bool
    defaultOption: str | list[str]


FieldTypeLiteral = Literal["text", "number", "textarea", "dropdown"]


FieldConfig = TextFieldConfig | NumberFieldConfig | TextareaFieldConfig | DropdownFieldConfig


class FieldSchema(TypedDict):
    id: str
    type: FieldTypeLiteral
    label: str
    question: str | None
    required: bool
    helpText: str | None
    placeholder: str | None
    defaultValue: str | None
    position: int
    config: FieldConfig


class FormMetadata(TypedDict):
    name: str
    slug: str
    description: str
    status: str


class FormSchema(TypedDict):
    form: FormMetadata
    fields: list[FieldSchema]
