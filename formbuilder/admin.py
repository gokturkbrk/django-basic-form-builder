from __future__ import annotations

import contextlib

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import CustomForm, FieldOption, FormField


class FieldOptionInline(admin.TabularInline):
    model = FieldOption
    extra = 1
    fields = ("value", "label", "position", "is_default")
    ordering = ("position", "id")


class FormFieldInlineForm(forms.ModelForm):
    # Text field config
    min_length = forms.IntegerField(
        required=False,
        label="Min Length",
        help_text="Minimum number of characters (for text/textarea)",
    )
    max_length = forms.IntegerField(
        required=False,
        label="Max Length",
        help_text="Maximum number of characters (for text/textarea)",
    )

    # Number field config
    min_value = forms.FloatField(
        required=False, label="Min Value", help_text="Minimum value (for number fields)"
    )
    max_value = forms.FloatField(
        required=False, label="Max Value", help_text="Maximum value (for number fields)"
    )
    step = forms.FloatField(
        required=False, label="Step", help_text="Increment step (for number fields)"
    )

    # Rating field config
    rating_scale = forms.ChoiceField(
        choices=[("", "---"), (5, "5 Stars"), (10, "10 Points")],
        required=False,
        label="Rating Scale",
        help_text="Scale for rating fields",
    )
    rating_style = forms.ChoiceField(
        choices=[("", "---"), ("stars", "Stars"), ("numeric", "Numeric"), ("emoji", "Emoji")],
        required=False,
        label="Rating Style",
        help_text="Display style for rating fields",
    )

    # Advanced config (JSON for other settings)
    config = forms.JSONField(
        required=False,
        help_text=(
            "Advanced configuration in JSON format. Available attributes by field type:\n\n"
            "• text: minLength, maxLength, pattern, inputMode (text/email/tel/url), prefix, suffix\n"
            "• number: min, max, step, prefix, suffix, unit\n"
            "• textarea: rows, minLength, maxLength, autoResize (true/false)\n"
            "• dropdown/radio: allowOther (true/false), allowMultiple (true/false for dropdown)\n"
            "• checkbox: minSelections, maxSelections, allowOther (true/false)\n"
            "• rating: scale (5 or 10), style (stars/numeric/emoji), minLabel, maxLabel\n"
            "• boolean: trueLabel, falseLabel, style (checkbox/toggle/radio)\n"
            "• email: confirmEmail (true/false)\n"
            "• date: minDate (YYYY-MM-DD), maxDate (YYYY-MM-DD), format (date format string)\n\n"
            'Note: For dropdown/radio/checkbox options, click "Save and continue editing" then use the "Field options" section below.'
        ),
        widget=forms.Textarea(
            attrs={"rows": 4, "style": "font-family: monospace; font-size: 12px;"}
        ),
    )

    class Meta:
        model = FormField
        fields = [
            "custom_form",
            "label",
            "slug",
            "question",
            "field_type",
            "position",
            "required",
            "help_text",
            "placeholder",
            "default_value",
            "config",
            "min_length",
            "max_length",
            "min_value",
            "max_value",
            "step",
            "rating_scale",
            "rating_style",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate config fields from JSON
        if self.instance and self.instance.config:
            config = self.instance.config
            self.fields["min_length"].initial = config.get("minLength")
            self.fields["max_length"].initial = config.get("maxLength")
            self.fields["min_value"].initial = config.get("min")
            self.fields["max_value"].initial = config.get("max")
            self.fields["step"].initial = config.get("step")
            self.fields["rating_scale"].initial = config.get("scale")
            self.fields["rating_style"].initial = config.get("style")

    def clean_config(self):
        """Ensure config is always a dict, never None."""
        config = self.cleaned_data.get("config") or {}
        if config == "":
            config = {}
        return config

    def clean(self):
        cleaned_data = super().clean()
        field_type = cleaned_data.get("field_type")
        config = cleaned_data.get("config") or {}

        # Only merge and validate config for the appropriate field types
        # Merge simple fields into config based on field type
        if field_type in [FormField.FieldType.TEXT, FormField.FieldType.TEXTAREA]:
            if cleaned_data.get("min_length") is not None:
                config["minLength"] = cleaned_data["min_length"]
            if cleaned_data.get("max_length") is not None:
                config["maxLength"] = cleaned_data["max_length"]
            # Clear non-applicable configs
            for key in ["min", "max", "step", "scale", "style"]:
                config.pop(key, None)

        elif field_type == FormField.FieldType.NUMBER:
            if cleaned_data.get("min_value") is not None:
                config["min"] = cleaned_data["min_value"]
            if cleaned_data.get("max_value") is not None:
                config["max"] = cleaned_data["max_value"]
            if cleaned_data.get("step") is not None:
                config["step"] = cleaned_data["step"]
            # Clear non-applicable configs
            for key in ["minLength", "maxLength", "scale", "style"]:
                config.pop(key, None)

        elif field_type == FormField.FieldType.RATING:
            if cleaned_data.get("rating_scale"):
                config["scale"] = int(cleaned_data["rating_scale"])
            if cleaned_data.get("rating_style"):
                config["style"] = cleaned_data["rating_style"]
            # Clear non-applicable configs
            for key in ["minLength", "maxLength", "min", "max", "step"]:
                config.pop(key, None)

        else:
            # For other field types, clear all the simple config fields
            for key in ["minLength", "maxLength", "min", "max", "step", "scale", "style"]:
                config.pop(key, None)

        cleaned_data["config"] = config
        return cleaned_data


class FormFieldInline(admin.StackedInline):
    model = FormField
    form = FormFieldInlineForm
    extra = 0
    ordering = ("position", "id")
    classes = ("collapse-open",)
    readonly_fields = ("manage_options_link",)

    def manage_options_link(self, obj):
        if obj.pk and obj.field_type in (
            FormField.FieldType.DROPDOWN,
            FormField.FieldType.RADIO,
            FormField.FieldType.CHECKBOX,
        ):
            list_url = (
                reverse("admin:formbuilder_fieldoption_changelist") + f"?field__id__exact={obj.pk}"
            )
            add_url = reverse("admin:formbuilder_fieldoption_add") + f"?field={obj.pk}"
            count = obj.options.count()
            return format_html(
                '<a href="{}" class="button" target="_blank" style="margin-right: 10px;">View Options ({})</a>'
                '<a href="{}" class="button addlink" target="_blank">Add New Option</a>',
                list_url,
                count,
                add_url,
            )
        return "-"

    manage_options_link.short_description = "Field Options"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("label", "slug"),
                    "question",
                    ("field_type", "position", "required"),
                    "manage_options_link",
                )
            },
        ),
        (
            "Display Options",
            {
                "fields": (
                    "placeholder",
                    "default_value",
                    "help_text",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Text/Textarea Configuration",
            {
                "fields": (("min_length", "max_length"),),
                "classes": ("collapse",),
                "description": "For text and textarea fields - other fields will ignore these",
            },
        ),
        (
            "Number Configuration",
            {
                "fields": (("min_value", "max_value", "step"),),
                "classes": ("collapse",),
                "description": "For number fields only - other fields will ignore these",
            },
        ),
        (
            "Rating Configuration",
            {
                "fields": (("rating_scale", "rating_style"),),
                "classes": ("collapse",),
                "description": "For rating fields only - other fields will ignore these",
            },
        ),
        (
            "Advanced Configuration",
            {
                "fields": ("config",),
                "classes": ("collapse",),
                "description": "For advanced users - JSON configuration with all available options",
            },
        ),
    )

    def get_formset(self, request, obj=None, **kwargs):
        """Customize the formset to include helpful attributes"""
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(CustomForm)
class CustomFormAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "updated_at", "preview_link")
    search_fields = ("name", "slug")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (FormFieldInline,)
    readonly_fields = ("preview_link",)

    class Media:
        css = {"all": ("formbuilder/admin/css/formfield_admin.css",)}
        js = ("formbuilder/admin/js/formfield_admin.js",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.generate_schema(commit=True)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:pk>/preview/",
                self.admin_site.admin_view(self.preview_view),
                name="formbuilder_customform_preview",
            ),
        ]
        return custom_urls + urls

    def preview_link(self, obj: CustomForm) -> str:
        if not obj.pk:
            return "Preview available after saving"
        url = reverse("admin:formbuilder_customform_preview", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Preview JSON</a>', url)

    preview_link.short_description = "JSON Preview"

    def preview_view(self, request, pk, *args, **kwargs):
        custom_form = get_object_or_404(CustomForm, pk=pk)
        if not custom_form.json_schema:
            custom_form.generate_schema(commit=True)
        return JsonResponse(custom_form.json_schema)


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    form = FormFieldInlineForm
    list_display = ("label", "custom_form", "field_type", "position", "required")
    list_filter = ("field_type", "required", "custom_form")
    search_fields = ("label", "slug", "question", "custom_form__name", "custom_form__slug")
    ordering = ("custom_form", "position")
    inlines = (FieldOptionInline,)

    class Media:
        js = ("formbuilder/admin/js/formfield_admin.js",)

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("custom_form", "label", "slug", "field_type", "position", "required")},
        ),
        (
            "Question/Description",
            {
                "fields": ("question",),
                "description": "Detailed question or explanation shown to users in feedback forms",
            },
        ),
        ("Display", {"fields": ("placeholder", "help_text", "default_value")}),
        (
            "Text/Textarea Configuration",
            {
                "fields": ("min_length", "max_length"),
                "classes": ("collapse",),
                "description": "For text and textarea fields only",
            },
        ),
        (
            "Number Configuration",
            {
                "fields": ("min_value", "max_value", "step"),
                "classes": ("collapse",),
                "description": "For number fields only",
            },
        ),
        (
            "Rating Configuration",
            {
                "fields": ("rating_scale", "rating_style"),
                "classes": ("collapse",),
                "description": "For rating fields only",
            },
        ),
        (
            "Advanced Configuration",
            {
                "fields": ("config",),
                "classes": ("collapse",),
                "description": "JSON configuration for advanced settings",
            },
        ),
    )


@admin.register(FieldOption)
class FieldOptionAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "field", "position", "is_default")
    list_filter = ("field__field_type", "field__custom_form", "is_default")
    search_fields = ("label", "value", "field__label", "field__slug")
    ordering = ("field", "position")
    list_editable = ("position",)
    actions = ["set_as_default"]

    def set_as_default(self, request, queryset):
        """Set selected option as default (clears other defaults for same field)"""
        if queryset.count() != 1:
            self.message_user(
                request, "Please select exactly one option to set as default.", level="ERROR"
            )
            return

        option = queryset.first()
        field = option.field

        # Check if field type supports single default only
        if field.field_type in (FormField.FieldType.DROPDOWN, FormField.FieldType.RADIO):
            # Clear other defaults for this field
            FieldOption.objects.filter(field=field).update(is_default=False)

        # Set this one as default
        option.is_default = True
        option.save()

        self.message_user(request, f'"{option.label}" set as default for {field.label}')

    set_as_default.short_description = "Set selected option as default"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "field",
                    ("value", "label"),
                    ("position", "is_default"),
                ),
                "description": "Note: For dropdown and radio fields, only one option can be marked as default.",
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ("field",)  # Don't allow changing the parent field
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit field selection to only dropdown, radio, and checkbox types"""
        if db_field.name == "field":
            kwargs["queryset"] = FormField.objects.filter(
                field_type__in=[
                    FormField.FieldType.DROPDOWN,
                    FormField.FieldType.RADIO,
                    FormField.FieldType.CHECKBOX,
                ]
            )
            # Pre-select field if passed in URL parameter
            field_id = request.GET.get("field")
            if field_id:
                with contextlib.suppress(FormField.DoesNotExist, ValueError):
                    kwargs["initial"] = FormField.objects.get(pk=field_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Add helpful context to the change form"""
        extra_context = extra_context or {}
        if not object_id:  # Adding new
            field_id = request.GET.get("field")
            if field_id:
                try:
                    field = FormField.objects.get(pk=field_id)
                    extra_context["subtitle"] = f"Adding option for: {field.label}"
                except (FormField.DoesNotExist, ValueError):
                    pass
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """Handle validation errors gracefully"""
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            # Re-raise to show proper error message
            from django.contrib import messages

            for field, errors in e.error_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            raise
