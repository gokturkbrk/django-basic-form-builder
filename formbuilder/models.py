from __future__ import annotations

from collections.abc import Iterable
from numbers import Number
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomForm(models.Model):
    class FormStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=FormStatus.choices,
        default=FormStatus.DRAFT,
    )
    json_schema = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        update_schema = kwargs.pop("update_schema", True)
        self.full_clean()
        super().save(*args, **kwargs)
        if update_schema:
            self.generate_schema(commit=True)

    def generate_schema(self, commit: bool = True) -> dict[str, Any]:
        from .services.schema_builder import SchemaBuilder

        schema = SchemaBuilder().build(self)
        if commit and self.pk:
            type(self).objects.filter(pk=self.pk).update(json_schema=schema)
            self.json_schema = schema
        return schema


class FormField(models.Model):
    class FieldType(models.TextChoices):
        TEXT = "text", _("Text Input")
        NUMBER = "number", _("Number Input")
        TEXTAREA = "textarea", _("Textarea")
        DROPDOWN = "dropdown", _("Dropdown")
        RADIO = "radio", _("Radio Buttons")
        CHECKBOX = "checkbox", _("Checkboxes")
        RATING = "rating", _("Rating Scale")
        BOOLEAN = "boolean", _("Yes/No")
        EMAIL = "email", _("Email Address")
        DATE = "date", _("Date Picker")

    FIELD_CONFIG_SCHEMA: dict[str, dict[str, Iterable[type]]] = {
        FieldType.TEXT: {
            "minLength": (int,),
            "maxLength": (int,),
            "pattern": (str,),
            "inputMode": (str,),
            "prefix": (str,),
            "suffix": (str,),
        },
        FieldType.NUMBER: {
            "min": (int, float, Number),
            "max": (int, float, Number),
            "step": (int, float, Number),
            "prefix": (str,),
            "suffix": (str,),
            "unit": (str,),
        },
        FieldType.TEXTAREA: {
            "rows": (int,),
            "minLength": (int,),
            "maxLength": (int,),
            "autoResize": (bool,),
        },
        FieldType.DROPDOWN: {
            "allowMultiple": (bool,),
            "allowOther": (bool,),
        },
        FieldType.RADIO: {
            "allowOther": (bool,),
        },
        FieldType.CHECKBOX: {
            "minSelections": (int,),
            "maxSelections": (int,),
            "allowOther": (bool,),
        },
        FieldType.RATING: {
            "scale": (int,),
            "style": (str,),
            "minLabel": (str,),
            "maxLabel": (str,),
        },
        FieldType.BOOLEAN: {
            "trueLabel": (str,),
            "falseLabel": (str,),
            "style": (str,),
        },
        FieldType.EMAIL: {
            "confirmEmail": (bool,),
        },
        FieldType.DATE: {
            "minDate": (str,),
            "maxDate": (str,),
            "format": (str,),
        },
    }

    custom_form = models.ForeignKey(
        CustomForm,
        related_name="fields",
        on_delete=models.CASCADE,
    )
    label = models.CharField(max_length=255, help_text="Short field label shown in forms")
    question = models.TextField(
        blank=True, help_text="Detailed question or explanation shown to users"
    )
    slug = models.SlugField()
    field_type = models.CharField(max_length=20, choices=FieldType.choices)
    position = models.PositiveIntegerField(default=1)
    required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=512, blank=True)
    placeholder = models.CharField(max_length=255, blank=True)
    default_value = models.CharField(max_length=255, blank=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("custom_form", "slug"),
                name="unique_field_slug_per_form",
            ),
            models.UniqueConstraint(
                fields=("custom_form", "position"),
                name="unique_field_position_per_form",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.label} ({self.custom_form.slug})"

    def clean(self) -> None:
        super().clean()
        # Ensure config is never None
        if self.config is None:
            self.config = {}
        self._validate_config_dict()
        self._validate_type_specific_rules()

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Ensure config is never None before saving
        if self.config is None:
            self.config = {}
        self.full_clean()
        super().save(*args, **kwargs)
        self.custom_form.generate_schema(commit=True)

    def delete(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - trivial
        custom_form = self.custom_form
        super().delete(*args, **kwargs)
        custom_form.generate_schema(commit=True)

    def _validate_config_dict(self) -> None:
        config = self.config or {}
        if not isinstance(config, dict):
            raise ValidationError({"config": _("Config must be an object.")})

        allowed_keys = set(self.FIELD_CONFIG_SCHEMA.get(self.field_type, {}))
        invalid_keys = set(config.keys()) - allowed_keys
        if invalid_keys:
            raise ValidationError(
                {
                    "config": _("Unsupported config keys: %(keys)s")
                    % {"keys": ", ".join(sorted(invalid_keys))}
                }
            )

        for key, allowed_types in self.FIELD_CONFIG_SCHEMA.get(self.field_type, {}).items():
            if key not in config:
                continue
            if not isinstance(config[key], tuple(allowed_types)):
                raise ValidationError(
                    {
                        "config": _("%(key)s must be of type %(types)s")
                        % {
                            "key": key,
                            "types": ", ".join(t.__name__ for t in allowed_types),
                        }
                    }
                )

    def _validate_type_specific_rules(self) -> None:
        config = self.config or {}
        if self.field_type == self.FieldType.TEXT:
            self._ensure_min_max_relationship(config, "minLength", "maxLength")
        elif self.field_type == self.FieldType.NUMBER:
            self._validate_numeric_config(config)
        elif self.field_type == self.FieldType.TEXTAREA:
            self._ensure_min_max_relationship(config, "minLength", "maxLength")
        elif self.field_type in (
            self.FieldType.DROPDOWN,
            self.FieldType.RADIO,
            self.FieldType.CHECKBOX,
        ):
            self._validate_option_field_config(config)
        elif self.field_type == self.FieldType.RATING:
            self._validate_rating_config(config)
        elif self.field_type == self.FieldType.DATE:
            self._validate_date_config(config)

    def _ensure_min_max_relationship(
        self, config: dict[str, Any], min_key: str, max_key: str
    ) -> None:
        min_value = config.get(min_key)
        max_value = config.get(max_key)
        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValidationError(
                {
                    "config": _("%(min_key)s cannot be greater than %(max_key)s.")
                    % {"min_key": min_key, "max_key": max_key}
                }
            )

    def _validate_numeric_config(self, config: dict[str, Any]) -> None:
        min_value = config.get("min")
        max_value = config.get("max")
        step = config.get("step")
        if step is not None and isinstance(step, Number) and step <= 0:
            raise ValidationError({"config": _("step must be greater than zero.")})
        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValidationError({"config": _("min cannot be greater than max.")})

    def _validate_option_field_config(self, config: dict[str, Any]) -> None:
        """Validate config for dropdown, radio, checkbox fields - options come from FieldOption model"""
        # Note: Actual options are validated through FieldOption model, not config
        # Config only contains behavior flags like allowMultiple, allowOther, etc.

        if self.field_type == self.FieldType.CHECKBOX:
            min_sel = config.get("minSelections")
            max_sel = config.get("maxSelections")
            if min_sel is not None and max_sel is not None and min_sel > max_sel:
                raise ValidationError(
                    {"config": _("minSelections cannot be greater than maxSelections.")}
                )

    def _validate_rating_config(self, config: dict[str, Any]) -> None:
        scale = config.get("scale")
        if scale is not None and scale not in (5, 10):
            raise ValidationError({"config": _("Rating scale must be 5 or 10.")})

        style = config.get("style")
        if style is not None and style not in ("stars", "numeric", "emoji"):
            raise ValidationError(
                {"config": _("Rating style must be one of: stars, numeric, emoji.")}
            )

    def _validate_date_config(self, config: dict[str, Any]) -> None:
        min_date = config.get("minDate")
        max_date = config.get("maxDate")
        # Basic validation - actual date parsing would happen in frontend/submission
        if min_date and max_date:
            # Could add date comparison if needed
            pass

    def _validate_dropdown_config(self, config: dict[str, Any]) -> None:
        """Legacy method - kept for backward compatibility with old config-based options"""
        options = config.get("options")
        if options:
            # If options are still in config (legacy), validate them
            if not isinstance(options, list):
                raise ValidationError({"config": _("options must be a list.")})
            normalized_options: list[str] = []
            for option in options:
                if not isinstance(option, dict):
                    raise ValidationError(
                        {"config": _("Each option must be an object with value and label.")}
                    )
                value = option.get("value")
                label = option.get("label")
                if not value or not label:
                    raise ValidationError(
                        {"config": _("Each option must include value and label.")}
                    )
                normalized_options.append(str(value))


class FieldOption(models.Model):
    """Options for dropdown, radio, and checkbox fields"""

    field = models.ForeignKey(
        FormField,
        related_name="options",
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=1)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ("position", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("field", "value"),
                name="unique_option_value_per_field",
            ),
            models.UniqueConstraint(
                fields=("field", "position"),
                name="unique_option_position_per_field",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.label} ({self.field.slug})"

    def clean(self) -> None:
        super().clean()
        # Validate that this field type supports options
        if self.field.field_type not in (
            FormField.FieldType.DROPDOWN,
            FormField.FieldType.RADIO,
            FormField.FieldType.CHECKBOX,
        ):
            raise ValidationError(
                {
                    "field": _(
                        f"Options are not supported for {self.field.get_field_type_display()} fields."
                    )
                }
            )
        if self.is_default and self.field.field_type in (
            FormField.FieldType.DROPDOWN,
            FormField.FieldType.RADIO,
        ):
            existing_defaults = self.field.options.exclude(pk=self.pk).filter(is_default=True)
            if existing_defaults.exists():
                raise ValidationError(
                    {"is_default": _("Only one default option is allowed for this field.")}
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
        # Regenerate schema when options change
        self.field.custom_form.generate_schema(commit=True)
