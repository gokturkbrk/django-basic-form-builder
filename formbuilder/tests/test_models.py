import pytest
from django.core.exceptions import ValidationError

from formbuilder.models import CustomForm, FieldOption, FormField


def test_generate_schema_updates_on_field_save(custom_form: CustomForm):
    FormField.objects.create(
        custom_form=custom_form,
        label="Full Name",
        slug="full_name",
        field_type=FormField.FieldType.TEXT,
        position=1,
        required=True,
        config={"minLength": 2, "maxLength": 120},
    )

    custom_form.refresh_from_db()
    schema = custom_form.json_schema
    assert schema["form"]["slug"] == "contact-form"
    assert schema["fields"][0]["config"]["minLength"] == 2
    assert schema["fields"][0]["type"] == FormField.FieldType.TEXT


def test_dropdown_can_have_options(custom_form: CustomForm):
    """Dropdown fields can have options via FieldOption model"""
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Country",
        slug="country",
        field_type=FormField.FieldType.DROPDOWN,
        position=1,
        required=True,
        config={},
    )

    # Add options via FieldOption model
    FieldOption.objects.create(field=field, value="us", label="United States", position=1)
    FieldOption.objects.create(field=field, value="ca", label="Canada", position=2, is_default=True)

    custom_form.refresh_from_db()
    schema = custom_form.json_schema
    field_schema = schema["fields"][0]
    assert field_schema["config"]["options"][0]["value"] == "us"
    assert field_schema["config"]["options"][1]["isDefault"] is True


def test_option_fields_require_options_before_publishing(custom_form: CustomForm):
    FormField.objects.create(
        custom_form=custom_form,
        label="Country",
        slug="country",
        field_type=FormField.FieldType.DROPDOWN,
        position=1,
    )

    custom_form.status = CustomForm.FormStatus.PUBLISHED
    with pytest.raises(ValidationError):
        custom_form.save()

    # Add an option and publishing should succeed
    field = custom_form.fields.get(slug="country")
    FieldOption.objects.create(field=field, value="us", label="United States", position=1)
    custom_form.save(update_schema=True)


def test_number_config_requires_valid_range(custom_form: CustomForm):
    field = FormField(
        custom_form=custom_form,
        label="Age",
        slug="age",
        field_type=FormField.FieldType.NUMBER,
        position=1,
        required=False,
        config={"min": 10, "max": 5},
    )

    with pytest.raises(ValidationError):
        field.full_clean()


def test_number_step_must_be_positive(custom_form: CustomForm):
    field = FormField(
        custom_form=custom_form,
        label="Salary",
        slug="salary",
        field_type=FormField.FieldType.NUMBER,
        position=1,
        config={"step": 0},
    )

    with pytest.raises(ValidationError):
        field.full_clean()


def test_checkbox_min_max_validation(custom_form: CustomForm):
    field = FormField(
        custom_form=custom_form,
        label="Interests",
        slug="interests",
        field_type=FormField.FieldType.CHECKBOX,
        position=1,
        config={"minSelections": 3, "maxSelections": 1},
    )

    with pytest.raises(ValidationError):
        field.full_clean()


def test_textarea_min_length_validation(custom_form: CustomForm):
    field = FormField(
        custom_form=custom_form,
        label="Message",
        slug="message",
        field_type=FormField.FieldType.TEXTAREA,
        position=1,
        config={"minLength": 200, "maxLength": 100},
    )

    with pytest.raises(ValidationError):
        field.full_clean()


def test_field_option_validates_field_type(custom_form: CustomForm):
    """FieldOption can only be added to dropdown, radio, or checkbox fields"""
    text_field = FormField.objects.create(
        custom_form=custom_form,
        label="Name",
        slug="name",
        field_type=FormField.FieldType.TEXT,
        position=1,
    )

    option = FieldOption(field=text_field, value="test", label="Test", position=1)

    with pytest.raises(ValidationError):
        option.full_clean()


def test_dropdown_multiple_defaults_in_schema(custom_form: CustomForm):
    """Multiple default options for checkbox or dropdown with allowMultiple"""
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Topics",
        slug="topics",
        field_type=FormField.FieldType.CHECKBOX,
        position=1,
        config={},
    )

    FieldOption.objects.create(field=field, value="news", label="News", position=1, is_default=True)
    FieldOption.objects.create(
        field=field, value="updates", label="Updates", position=2, is_default=True
    )
    FieldOption.objects.create(field=field, value="other", label="Other", position=3)

    custom_form.refresh_from_db()
    schema = custom_form.json_schema
    field_schema = schema["fields"][0]
    assert field_schema["config"]["defaultOption"] == ["news", "updates"]


def test_radio_allows_only_single_default(custom_form: CustomForm):
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Satisfaction",
        slug="satisfaction",
        field_type=FormField.FieldType.RADIO,
        position=1,
    )

    FieldOption.objects.create(
        field=field, value="happy", label="Happy", position=1, is_default=True
    )
    with pytest.raises(ValidationError):
        FieldOption.objects.create(
            field=field,
            value="sad",
            label="Sad",
            position=2,
            is_default=True,
        )


def test_rating_config_validation(custom_form: CustomForm):
    invalid_scale = FormField(
        custom_form=custom_form,
        label="Experience",
        slug="experience",
        field_type=FormField.FieldType.RATING,
        position=1,
        config={"scale": 7},
    )
    with pytest.raises(ValidationError):
        invalid_scale.full_clean()

    invalid_style = FormField(
        custom_form=custom_form,
        label="Experience 2",
        slug="experience-2",
        field_type=FormField.FieldType.RATING,
        position=2,
        config={"scale": 5, "style": "hearts"},
    )
    with pytest.raises(ValidationError):
        invalid_style.full_clean()

    valid = FormField(
        custom_form=custom_form,
        label="Experience 3",
        slug="experience-3",
        field_type=FormField.FieldType.RATING,
        position=3,
        config={"scale": 5, "style": "stars"},
    )
    valid.full_clean()


def test_radio_cannot_have_multiple_defaults(custom_form: CustomForm):
    """Radio fields can only have one default option"""
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Gender",
        slug="gender",
        field_type=FormField.FieldType.RADIO,
        position=1,
    )

    FieldOption.objects.create(field=field, value="m", label="Male", position=1, is_default=True)

    # Try to create another default - should fail
    option2 = FieldOption(field=field, value="f", label="Female", position=2, is_default=True)

    with pytest.raises(ValidationError) as exc_info:
        option2.full_clean()

    assert "is_default" in exc_info.value.error_dict
    assert "Only one default option is allowed for this field." in str(exc_info.value)


def test_dropdown_cannot_have_multiple_defaults(custom_form: CustomForm):
    """Dropdown fields (single-select) can only have one default option"""
    field = FormField.objects.create(
        custom_form=custom_form,
        label="Country",
        slug="country",
        field_type=FormField.FieldType.DROPDOWN,
        position=1,
    )

    FieldOption.objects.create(field=field, value="us", label="USA", position=1, is_default=True)

    # Try to create another default - should fail
    option2 = FieldOption(field=field, value="ca", label="Canada", position=2, is_default=True)

    with pytest.raises(ValidationError) as exc_info:
        option2.full_clean()

    assert "is_default" in exc_info.value.error_dict
    assert "Only one default option is allowed for this field." in str(exc_info.value)
