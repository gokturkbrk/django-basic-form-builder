# Changelog

All notable changes to django-formbuilder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-09

### Added

#### Core Features

- **Dynamic Form Builder**: Create and manage custom forms entirely through Django admin
- **JSON Schema Generation**: Automatic JSON schema generation for frontend consumption
- **REST API Endpoint**: Read-only API at `/api/forms/<slug>/` for published forms
- **Admin Preview**: In-admin JSON preview link for instant schema inspection

#### Data Models

- `CustomForm` model with name, slug, description, status (draft/published), and JSON schema storage
- `FormField` model with comprehensive configuration options
- `FieldOption` model for managing dropdown, radio, and checkbox options via inline admin

#### Field Types

- **Text**: Single-line text input with minLength, maxLength, pattern, inputMode, prefix, suffix
- **Number**: Numeric input with min, max, step, unit validation
- **Textarea**: Multi-line text with rows, minLength, maxLength, autoResize
- **Dropdown**: Single or multiple selection with options from FieldOption model
- **Radio**: Single selection with radio button UI, options from FieldOption model
- **Checkbox**: Multi-select with minSelections, maxSelections constraints
- **Rating**: 1-5 or 1-10 scale with stars/numeric/emoji styles
- **Boolean**: Yes/No or True/False toggle with custom labels
- **Email**: Email validation with optional confirm email field
- **Date**: Date picker with minDate, maxDate, format configuration

#### Admin UX

- **Stacked Inline Editor**: Enhanced form field editing with visual separation
- **Label vs Question Fields**:
  - Label: Short technical identifier for compact UIs
  - Question: Detailed user-facing text for feedback forms
- **Auto-positioning**: Automatic position field updates when adding/removing fields
- **Type-specific Configuration**: Dedicated config sections for text/number/rating fields
- **Field Option Management**: Inline editor for dropdown/radio/checkbox options
- **Visual Improvements**:
  - 3px borders and shadows for field separation
  - Expandable/collapsible fieldsets with arrow icons
  - Gradient backgrounds and hover effects
  - Clear help text for all configuration options

#### Schema Builder Service

- Pure Python `SchemaBuilder` service with zero Django dependencies
- `CustomForm.generate_schema()` wrapper for automatic schema regeneration
- Attribute whitelisting per field type
- Validation for type-specific rules (min/max relationships, option constraints)

#### Testing & Quality

- Comprehensive test suite with pytest and pytest-django
- 100% test coverage for core functionality
- Unit tests for all field types and validation rules
- API endpoint tests (happy path, 404, feature flag)
- Admin validation tests
- Schema generation tests

#### Developer Experience

- Pre-commit hooks with ruff linting and formatting
- Type hints throughout codebase
- Comprehensive documentation in README
- Sample fixture (`demo_form.json`) with all field types
- Technical architecture documentation
- Configuration guide for host projects

#### Compatibility

- Django 5.1+ support
- Django REST Framework 3.15+ integration
- Python 3.12+ compatibility
- Python 3.14 compatibility patch for template context bug

### Configuration

- `FORMBUILDER_API_ENABLED`: Feature flag to enable/disable API (default: False; opt-in by setting `FORMBUILDER_API_ENABLED = True`)
- Automatic schema regeneration on form/field/option save
- Unique constraints for slugs and positions per form

### Documentation

- Complete README with installation, usage, and API documentation
- Field attribute matrix showing all config options per type
- Label vs Question usage guide
- Quick start guide with step-by-step examples
- JSON schema contract documentation
- Testing instructions

### Dependencies

- Django >= 5.1, < 5.2
- djangorestframework >= 3.15.0
- drf-spectacular >= 0.29.0 (API documentation)
- Optional extras: `postgres` installs psycopg[binary]>=3.2.0, `html` installs nh3>=0.3.2

### Development Dependencies

- pytest >= 8.0.0
- pytest-django >= 4.8.0
- pytest-cov >= 5.0.0
- ruff >= 0.5.0 (linting and formatting)
- mypy >= 1.11.0 (type checking)

[0.1.0]: https://github.com/yourusername/django-formbuilder/releases/tag/v0.1.0
