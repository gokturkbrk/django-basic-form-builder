# Release Notes - v0.1.0

## Overview

This is the initial release of django-formbuilder, a reusable Django app that enables dynamic form creation through the Django admin with JSON schema generation for frontend consumption.

## What's Completed ✅

### Core Features

- ✅ Full form builder functionality in Django admin
- ✅ 10 field types with comprehensive validation
- ✅ REST API endpoint for published forms
- ✅ Automatic JSON schema generation
- ✅ Admin preview functionality
- ✅ FieldOption model for dropdown/radio/checkbox options
- ✅ Comprehensive test suite (21 tests, 82% coverage)
- ✅ Type hints throughout codebase
- ✅ Linting with ruff configured
- ✅ Pre-commit hooks set up
- ✅ Complete documentation (README, CHANGELOG, technical architecture)
- ✅ Demo fixture with all field types

### Field Types Implemented

1. Text - with min/max length, pattern validation
2. Number - with min/max/step validation
3. Textarea - multi-line with config
4. Dropdown - single or multiple selection
5. Radio - single choice with radio UI
6. Checkbox - multi-select with constraints
7. Rating - star/numeric/emoji scales
8. Boolean - yes/no toggles
9. Email - with validation
10. Date - date picker

### Admin UX Enhancements

- ✅ Stacked inline editor with visual separation
- ✅ Label vs Question fields for different contexts
- ✅ Auto-positioning for form fields
- ✅ Type-specific configuration sections
- ✅ Field option management for selection fields
- ✅ Expandable/collapsible fieldsets
- ✅ Preview JSON link

## Deployment Checklist 📋

The following tasks should be completed during deployment to production:

### Pre-Deployment

- [ ] Review and test the demo form locally
- [ ] Verify all migrations are in place
- [ ] Run full test suite: `uv run pytest`
- [ ] Check linting: `uv run ruff check .`
- [ ] Build distribution packages: `python -m build`
- [ ] Smoke test the built wheel/sdist

### Deployment

- [ ] Apply migrations on staging: `python manage.py migrate`
- [ ] Load demo form if desired: `python manage.py loaddata formbuilder/fixtures/demo_form.json`
- [ ] Create Django admin superuser: `python manage.py createsuperuser`
- [ ] Verify admin access at `/admin/formbuilder/`
- [ ] Test form creation in admin
- [ ] Test API endpoint: `curl http://your-domain/api/forms/<slug>/`
- [ ] Verify Python 3.14 compatibility patch loads (if on Python 3.14)

### Post-Deployment

- [ ] Create test form in production admin
- [ ] Verify JSON schema generation
- [ ] Test API endpoint with published form
- [ ] Monitor error logs for any issues
- [ ] Document any production-specific configuration

### Release

- [ ] Tag release in git: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Publish to PyPI (if applicable): `python -m twine upload dist/*`
- [ ] Create GitHub release with CHANGELOG
- [ ] Update documentation links

## Configuration Notes

### Required Settings

Add to your Django `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'formbuilder',
    # ...
]
```

### Optional Settings

```python
# Disable API endpoint globally (default: True)
FORMBUILDER_API_ENABLED = False
```

### URL Configuration

```python
urlpatterns = [
    path('api/forms/', include('formbuilder.api.urls')),
]
```

## Known Issues

- Admin coverage is at 49% - most untested paths are UI-related admin methods that are difficult to test with Django's test client. Consider functional testing for full coverage.
- Some model methods marked as "pragma: no cover" are trivial (delete, __str__)
- Python 3.14 requires compatibility patch (automatically applied)

## Future Enhancements (Out of Scope for v0.1.0)

- [ ] File upload field type
- [ ] Field dependencies/conditional logic
- [ ] Form submission handling/storage
- [ ] Email notifications on submission
- [ ] Form analytics/metrics
- [ ] Multi-page forms
- [ ] Field validation rules (regex, custom)
- [ ] Theme/style customization
- [ ] Export forms as PDF
- [ ] Form versioning
- [ ] A/B testing support

## Support

For issues, questions, or contributions, please refer to:

- README.md - Installation and usage
- TECHNICAL_ARCHITECTURE.md - Architecture details
- CONFIGURATION_GUIDE.md - Integration guide
- TASK_LIST.md - Development history

## Version Information

- __Version__: 0.1.0
- __Release Date__: February 9, 2026
- __Django__: 5.1+
- __DRF__: 3.15+
- __Python__: 3.12+
