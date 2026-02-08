from formbuilder.models import CustomForm, FieldOption, FormField
from formbuilder.services.schema_builder import SchemaBuilder


def test_schema_builder_outputs_expected_payload(custom_form: CustomForm):
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Country",
        slug="country",
        field_type=FormField.FieldType.DROPDOWN,
        position=2,
        config={"allowMultiple": False},
    )
    # Add options via FieldOption model
    FieldOption.objects.create(field=field, value="us", label="United States", position=1)
    FieldOption.objects.create(field=field, value="ca", label="Canada", position=2)

    FormField.objects.create(
        custom_form=custom_form,
        label="Email",
        slug="email",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"inputMode": "email"},
    )

    schema = SchemaBuilder().build(custom_form)
    assert schema["form"]["name"] == "Contact Form"
    assert [f["id"] for f in schema["fields"]] == ["email", "country"]
    dropdown = schema["fields"][1]
    assert dropdown["config"]["options"][0]["value"] == "us"
    assert dropdown["config"]["options"][0]["label"] == "United States"
    assert dropdown["config"]["allowMultiple"] is False
    assert "position" in dropdown


def test_schema_includes_question_and_scalar_default(custom_form: CustomForm):
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Country",
        question="What country do you live in?",
        slug="country",
        field_type=FormField.FieldType.DROPDOWN,
        position=1,
    )
    FieldOption.objects.create(
        field=field, value="us", label="United States", position=1, is_default=True
    )

    schema = SchemaBuilder().build(custom_form)
    field_schema = schema["fields"][0]
    assert field_schema["question"] == "What country do you live in?"
    assert field_schema["config"]["defaultOption"] == "us"
