from django.apps import AppConfig


class FormbuilderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "formbuilder"

    def ready(self):  # type: ignore[override]
        from .compat import patch_template_context_copy

        patch_template_context_copy()
