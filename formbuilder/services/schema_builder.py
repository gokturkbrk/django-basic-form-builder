from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import CustomForm, FormField
from ..schema_types import FieldConfig, FieldSchema, FormSchema


class SchemaBuilder:
    """Builds the JSON schema snapshot stored on ``CustomForm``."""

    def build(self, custom_form: CustomForm) -> FormSchema:
        form_payload = {
            "name": custom_form.name,
            "slug": custom_form.slug,
            "description": custom_form.description,
            "status": custom_form.status,
        }
        require_options = custom_form.status == CustomForm.FormStatus.PUBLISHED
        fields_payload = [
            self._serialize_field(field, require_options)
            for field in custom_form.fields.all().order_by("position", "id")
        ]
        return {"form": form_payload, "fields": fields_payload}

    def _serialize_field(self, field: FormField, require_options: bool) -> FieldSchema:
        payload: FieldSchema = {
            "id": field.slug,
            "type": field.field_type,
            "label": field.label,
            "question": field.question or None,
            "required": field.required,
            "helpText": field.help_text or None,
            "placeholder": field.placeholder or None,
            "defaultValue": field.default_value or None,
            "position": field.position,
            "config": self._build_config(field, require_options),
        }
        return payload

    def _build_config(self, field: FormField, require_options: bool) -> FieldConfig:
        allowed_keys = field.FIELD_CONFIG_SCHEMA.get(field.field_type, {})
        config: dict[str, Any] = field.config or {}
        serialized: dict[str, Any] = {}

        # Copy allowed config keys
        for key in allowed_keys:
            if key in config:
                serialized[key] = deepcopy(config[key])

        # Add options from FieldOption model for dropdown, radio, checkbox fields
        option_field_types = (
            FormField.FieldType.DROPDOWN,
            FormField.FieldType.RADIO,
            FormField.FieldType.CHECKBOX,
        )

        if field.field_type in option_field_types:
            options = list(field.options.all().order_by("position", "id"))
            if options:
                serialized["options"] = [
                    {
                        "value": option.value,
                        "label": option.label,
                        "isDefault": option.is_default,
                    }
                    for option in options
                ]
                default_options = [opt.value for opt in options if opt.is_default]
                if default_options:
                    if field.field_type == FormField.FieldType.CHECKBOX or config.get(
                        "allowMultiple"
                    ):
                        serialized["defaultOption"] = default_options
                    else:
                        serialized["defaultOption"] = default_options[0]
            elif require_options:
                raise ValidationError(
                    {
                        "fields": _(
                            'Field "%(label)s" requires at least one option before publishing.'
                        )
                        % {"label": field.label}
                    }
                )

        return serialized  # type: ignore[return-value]
