# Quick Start Guide

This guide helps you get started with django-formbuilder development or integration.

## For Developers (Contributing to django-formbuilder)

### Initial Setup

1. **Clone and set up environment:**

   ```bash
   git clone <repository-url>
   cd django-basic-form-builder
   uv sync --group dev
   ```

2. **Run migrations:**

   ```bash
   uv run python manage.py migrate
   ```

3. **Load demo data:**

   ```bash
   uv run python manage.py loaddata formbuilder/fixtures/demo_form.json
   ```

4. **Create superuser:**

   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Start development server:**

   ```bash
   uv run python manage.py runserver
   ```

6. **Access admin:**
   Navigate to <http://localhost:8000/admin/formbuilder/>

### Development Workflow

1. **Run tests before making changes:**

   ```bash
   uv run pytest
   ```

2. **Make your changes**

3. **Check linting:**

   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

4. **Run tests again:**

   ```bash
   uv run pytest
   ```

5. **Install pre-commit hooks (first time):**

   ```bash
   uv tool install pre-commit
   pre-commit install
   ```

### Testing the API

```bash
# Generate schema for a form
uv run python manage.py shell -c "from formbuilder.models import CustomForm; CustomForm.objects.get(slug='contact-demo').generate_schema(commit=True)"

# Test the API endpoint
curl http://localhost:8000/api/forms/contact-demo/
```

## For Integrators (Using django-formbuilder in your project)

### Installation

1. **Install the package:**

   ```bash
   uv pip install django-formbuilder
   # or
   pip install django-formbuilder
   ```

2. **Add to INSTALLED_APPS** in `settings.py`:

   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'formbuilder',
       # ...
   ]
   ```

3. **Add URL patterns** in your project's `urls.py`:

   ```python
   from django.urls import include, path

   urlpatterns = [
       # ...
       path('api/forms/', include('formbuilder.api.urls')),
       # ...
   ]
   ```

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Optional - Load demo form:**

   ```bash
   python manage.py loaddata formbuilder/fixtures/demo_form.json
   ```

### Creating Your First Form

1. **Access Django Admin:**
   Navigate to `/admin/formbuilder/customform/`

2. **Add a new form:**
   - Name: "Contact Form"
   - Slug: "contact-form"
   - Description: "A simple contact form"
   - Status: "published"

3. **Add fields using the inline editor:**
   - Click "Add another Form field"
   - Fill in: Label, Question, Field Type, etc.
   - For dropdown/radio/checkbox: Save form, then edit the field to add options

4. **Preview the JSON:**
   - Click "Preview JSON" link in the admin
   - Or visit: `/api/forms/contact-form/`

### Fetching Forms in Your Frontend

```javascript
// Fetch form schema
const response = await fetch('/api/forms/contact-form/');
const formData = await response.json();

// formData.form contains form metadata
// formData.fields contains array of field definitions

// Render fields dynamically based on field type
formData.fields.forEach(field => {
  switch(field.type) {
    case 'text':
      // Render text input
      break;
    case 'dropdown':
      // Render select with field.config.options
      break;
    // ... handle other types
  }
});
```

## Common Tasks

### Run Tests with Coverage

```bash
uv run pytest -vv --cov=formbuilder --cov-report=term-missing
```

### Format Code

```bash
uv run ruff format .
```

### Fix Linting Issues

```bash
uv run ruff check . --fix
```

### Create a Migration

```bash
uv run python manage.py makemigrations formbuilder
```

### Build Distribution Packages

```bash
python -m build
```

### Check Package Contents

```bash
tar tzf dist/django-formbuilder-*.tar.gz
```

## Troubleshooting

### Issue: API returns empty schema `{}`

**Solution:** The schema hasn't been generated yet. Either:

- Save the form in admin (triggers auto-generation)
- Manually trigger: `form.generate_schema(commit=True)`

### Issue: Options not showing for dropdown field

**Solution:**

- Save the form first with "Save and continue editing"
- Click on the field to edit it individually
- Add options in the "Field options" inline section at the bottom

### Issue: Tests failing

**Solution:**

- Make sure you're in the right directory
- Run: `uv sync --group dev` to install dependencies
- Check that migrations are applied: `uv run python manage.py migrate`

### Issue: Linting errors

**Solution:**

- Auto-fix most issues: `uv run ruff check . --fix`
- Format code: `uv run ruff format .`

## Project Structure

```
formbuilder/
├── models.py              # CustomForm, FormField, FieldOption
├── admin.py               # Admin configuration
├── services/
│   └── schema_builder.py  # Schema generation logic
├── api/
│   ├── views.py           # API endpoints
│   ├── serializers.py     # DRF serializers
│   └── urls.py            # API URL routing
├── fixtures/
│   └── demo_form.json     # Sample form data
├── tests/                 # Test suite
└── static/formbuilder/admin/  # Admin CSS/JS

formbuilder_test_site/     # Test Django project
├── settings.py
└── urls.py
```

## Resources

- **README.md** - Complete feature documentation
- **TECHNICAL_ARCHITECTURE.md** - Architecture details
- **CONFIGURATION_GUIDE.md** - Integration guide
- **CHANGELOG.md** - Version history
- **RELEASE_NOTES.md** - Release information
- **TASK_LIST.md** - Development history

## Need Help?

1. Check the documentation files listed above
2. Look at the demo fixture for examples
3. Run tests to see usage patterns: `formbuilder/tests/`
4. Inspect the admin interface for UI patterns
