import pytest

from formbuilder.models import CustomForm


@pytest.fixture()
def custom_form(db) -> CustomForm:
    return CustomForm.objects.create(name="Contact Form", slug="contact-form")
