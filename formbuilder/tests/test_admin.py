from unittest import mock

from django.contrib import admin, auth
from django.test import Client
from django.urls import reverse

from formbuilder.admin import CustomFormAdmin
from formbuilder.models import CustomForm, FormField


class _DummyForm:
    def __init__(self, instance: CustomForm):
        self.instance = instance

    def save_m2m(self):  # pragma: no cover - trivial helper
        pass


def test_admin_save_related_regenerates_schema(custom_form: CustomForm):
    site = admin.sites.AdminSite()
    admin_view = CustomFormAdmin(CustomForm, site)
    mocked_generate = mock.MagicMock()
    custom_form.generate_schema = mocked_generate  # type: ignore[attr-defined]
    form = _DummyForm(instance=custom_form)

    admin_view.save_related(request=None, form=form, formsets=[], change=False)

    mocked_generate.assert_called_once_with(commit=True)


def test_preview_view_returns_json(custom_form: CustomForm, db):
    FormField.objects.create(
        custom_form=custom_form,
        label="Email",
        slug="email",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"inputMode": "email"},
    )
    custom_form.refresh_from_db()

    user_model = auth.get_user_model()
    user_model.objects.create_superuser(
        username="admin", email="admin@example.com", password="pass"
    )
    client = Client()
    assert client.login(username="admin", password="pass")

    url = reverse("admin:formbuilder_customform_preview", args=[custom_form.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["fields"][0]["id"] == "email"
