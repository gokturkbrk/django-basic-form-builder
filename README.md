# django-formbuilder

Reusable Django app that lets admins define JSON-rendered forms directly in the Django admin, then expose them via a read-only API endpoint. Works with Django 5.1+, DRF 3.15+, and the dependency stack listed in `pyproject.toml`.

## Installation

1. Install with [uv](https://github.com/astral-sh/uv) (preferred) or pip:

   ```bash
   uv pip install django-formbuilder
   ```

   Optional extras:

   - PostgreSQL support: `uv pip install "django-formbuilder[postgres]"`
   - HTML sanitization utilities (if you integrate them yourself): `uv pip install "django-formbuilder[html]"`

2. Add `formbuilder` (and `rest_framework` if not already present) to `INSTALLED_APPS`.
3. Explicitly enable the read-only API endpoint (it is off by default to avoid exposing form data unintentionally):

   ```python
   FORMBUILDER_API_ENABLED = True
   ```

4. Include the API URLs in your project routes:

   ```python
   from django.urls import include, path

   urlpatterns = [
       path('api/forms/', include('formbuilder.api.urls')),
   ]
   ```

5. Run migrations (`python manage.py migrate`).

## Admin Usage

- Create a **Custom Form** entry in admin (name, slug, description, status).
- Add **Form Fields** using the stacked inline editor; supported types are `text`, `number`, `textarea`, `dropdown`, `radio`, `checkbox`, `rating`, `boolean`, `email`, `date`.
- For each field:
  - **Label**: Short technical identifier (e.g., "Email", "Full Name") - used internally and in compact UIs
  - **Question**: Detailed question or explanation for users (e.g., "What is your email address? We'll use this to send you updates.")
    - For feedback forms, this is the primary text users see
    - Can be left blank if the label is self-explanatory
  - **Slug**: Technical field identifier (auto-generated from label)
  - Configure shared attributes (required, placeholder, default value, help text)
- For dropdown, radio, and checkbox fields:
  - After saving the form, click "Save and continue editing"
  - Click on a field to edit it individually
  - Use the "Field options" inline editor at the bottom to add options
- For text/number/rating fields:
  - Expand the relevant configuration section (Text/Number/Rating Configuration)
  - Use the dedicated config fields (min/max length, min/max value, rating scale)
  - These fields are type-specific and only apply to their respective field types
  - Or use the advanced JSON config section for power users
- **Position auto-update**: When you add or remove fields, positions are automatically renumbered (1, 2, 3, etc.)
- **Visual separation**: Each form field is shown in a separate bordered box for clarity
- On every save, the app regenerates a JSON snapshot stored on `CustomForm.json_schema`.
- Use the "Preview JSON" link to inspect the generated schema in a new tab.
- Running on Python 3.14? A compatibility shim automatically patches Django's template context copy routine.

### Label vs Question - When to Use Which?

**Label** (required):

- Short, concise identifier: "Email", "Phone", "Rating"
- Used in compact form layouts, tables, and admin interfaces
- Technical reference for developers
- Appears in form labels and summaries

**Question** (optional but recommended for feedback forms):

- Full question or detailed explanation: "How satisfied are you with our service?"
- Primary text shown to users in feedback/survey forms
- Can include context, examples, or instructions
- Better user experience for participation forms

**Example:**

```text
Label: "Service Quality"
Question: "On a scale of 1-5 stars, how would you rate the quality of service you received today?"

Label: "Email"
Question: "What email address should we use to send you updates about your inquiry?"
```

### Quick Start Guide

1. **Create a form in Django admin:**
   - Navigate to `/admin/formbuilder/customform/add/`
   - Fill in: Name = "Contact Us", Slug = "contact-us", Status = "published"
   - Click "Add another Form field" in the inline section:
     - Label = "Full Name"
     - Slug = "full_name"
     - Question = "What is your full name?"
     - Type = "text"
     - Required = ✓
   - Add another field:
     - Label = "Department"
     - Slug = "department"
     - Question = "Which department would you like to contact?"
     - Type = "dropdown"
   - Click "Save and continue editing"
   - Click on the Department field link to edit it
   - In the "Field options" section at the bottom, add:
     - Option 1: Value = "sales", Label = "Sales Team", Position = 1
     - Option 2: Value = "support", Label = "Customer Support", Position = 2
   - Add a rating field back in the main form:
     - Label = "Satisfaction"
     - Question = "How satisfied are you with our service?"
     - Type = "rating"
     - Expand "Rating Configuration" section
     - Set Scale = 5, Style = "stars"
   - Positions will auto-update as you add/remove fields
   - Save the form

2. **Fetch the JSON schema via API:**

   ```bash
   curl http://localhost:8000/api/forms/contact-us/
   ```

   You'll receive:

   ```json
   {
     "form": {
       "name": "Contact Us",
       "slug": "contact-us",
       "status": "published"
     },
     "fields": [
       {
         "id": "full_name",
         "type": "text",
         "label": "Full Name",
         "question": "What is your full name?",
         "required": true,
         "position": 1,
         ...
       },
       {
         "id": "department",
         "type": "dropdown",
         "label": "Department",
         "question": "Which department would you like to contact?",
         "config": {
           "options": [
             {"value": "sales", "label": "Sales Team", "isDefault": false},
             {"value": "support", "label": "Customer Support", "isDefault": false}
           ]
         },
         "position": 2,
         ...
       },
       {
         "id": "satisfaction",
         "type": "rating",
         "label": "Satisfaction",
         "question": "How satisfied are you with our service?",
         "config": {
           "scale": 5,
           "style": "stars"
         },
         "position": 3,
         ...
       }
     ]
   }
   ```

3. **Preview before publishing:**
   - While editing a form in admin, click the "Preview JSON" link to see the generated schema
   - Forms with `status="draft"` return 404 from the API but are visible in admin preview

## JSON Schema Contract

Returned from `/api/forms/<slug>/` when the form status is `published`.

```json
{
  "form": {
    "name": "Contact Us",
    "slug": "contact-us",
    "description": "Lead capture form",
    "status": "published"
  },
  "fields": [
    {
      "id": "full_name",
      "type": "text",
      "label": "Full Name",
      "required": true,
      "helpText": "As shown on ID",
      "placeholder": "Jane Doe",
      "defaultValue": null,
      "position": 1,
      "config": {
        "minLength": 2,
        "maxLength": 120,
        "inputMode": "text",
        "prefix": "",
        "suffix": ""
      }
    }
  ]
}
```

### Field Attribute Matrix

| Field Type | Config Keys | Notes |
| --- | --- | --- |
| `text` | `minLength`, `maxLength`, `pattern`, `inputMode`, `prefix`, `suffix` | Single-line text input |
| `number` | `min`, `max`, `step`, `prefix`, `suffix`, `unit` | Numeric input with validation |
| `textarea` | `rows`, `minLength`, `maxLength`, `autoResize` | Multi-line text input |
| `dropdown` | `allowMultiple`, `allowOther`, `options`, `defaultOption` | Options managed via FieldOption model (inline editor) |
| `radio` | `allowOther`, `options`, `defaultOption` | Single selection, options via FieldOption model |
| `checkbox` | `minSelections`, `maxSelections`, `allowOther`, `options`, `defaultOption` | Multiple selections, options via FieldOption model |
| `rating` | `scale` (5 or 10), `style` (stars/numeric/emoji), `minLabel`, `maxLabel` | Rating scale input |
| `boolean` | `trueLabel`, `falseLabel`, `style` | Yes/No or True/False |
| `email` | `confirmEmail` | Email with validation |
| `date` | `minDate`, `maxDate`, `format` | Date picker |

## Sample Fixture

Load an example form (Contact Us) into any project:

```bash
python manage.py loaddata formbuilder/fixtures/demo_form.json
```

The fixture seeds one published `CustomForm` with two fields (text + dropdown) so you can immediately hit `/api/forms/contact-demo/` and inspect the JSON. Use this as a template when sharing schemas with frontend teams.

## Testing Locally

This repo includes a tiny Django settings module (`formbuilder_test_site`) used only for running the test suite:

```bash
uv sync --group dev
pytest
```

The configured `pytest` run uses `-vv --cov=formbuilder --cov-report=term-missing`, so the CLI output lists each test, statuses, and line coverage to help you verify exactly what executed.

## Development Setup

To enable pre-commit hooks for linting and formatting:

```bash
uv tool install pre-commit
pre-commit install
```

## Feature Flag

Toggle the read-only API via the `FORMBUILDER_API_ENABLED` setting. The API is disabled unless you explicitly set `FORMBUILDER_API_ENABLED = True`; when left `False`, `/api/forms/<slug>/` returns 404 regardless of form status.

## Compatibility Notes

- Django 5.1 on Python 3.14 has a known bug in `django.template.context.BaseContext.__copy__`. This package patches the method at import time so admin pages continue to work. No action is required from host projects besides including `formbuilder` in `INSTALLED_APPS`.
