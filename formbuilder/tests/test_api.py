from django.test import override_settings
from rest_framework.test import APIClient

from formbuilder.models import CustomForm, FormField


def _publish_form(custom_form: CustomForm) -> CustomForm:
    custom_form.status = CustomForm.FormStatus.PUBLISHED
    custom_form.save()
    return custom_form


def test_api_returns_schema(custom_form: CustomForm):
    FormField.objects.create(
        custom_form=custom_form,
        label="Email",
        slug="email",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"inputMode": "email"},
    )
    _publish_form(custom_form)

    client = APIClient()
    response = client.get("/api/forms/contact-form/")

    assert response.status_code == 200
    assert response.json()["fields"][0]["id"] == "email"


@override_settings(FORMBUILDER_API_ENABLED=False)
def test_api_disabled_returns_404(custom_form: CustomForm):
    FormField.objects.create(
        custom_form=custom_form,
        label="Email",
        slug="email",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"inputMode": "email"},
    )
    _publish_form(custom_form)

    client = APIClient()
    response = client.get("/api/forms/contact-form/")

    assert response.status_code == 404


def test_api_filters_unpublished_forms(custom_form: CustomForm):
    FormField.objects.create(
        custom_form=custom_form,
        label="Email",
        slug="email",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"inputMode": "email"},
    )

    client = APIClient()
    response = client.get("/api/forms/contact-form/")

    assert response.status_code == 404
