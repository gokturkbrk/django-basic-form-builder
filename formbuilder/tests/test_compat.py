from copy import copy as copy_fn

from django.template.context import BaseContext

from formbuilder.compat import patch_template_context_copy


def test_patch_template_context_copy_replaces_impl(monkeypatch):
    original = BaseContext.__copy__
    patch_template_context_copy()

    ctx = BaseContext({"foo": "bar"})
    duplicate = copy_fn(ctx)
    assert duplicate.dicts == ctx.dicts

    # Restore for other tests
    monkeypatch.setattr(BaseContext, "__copy__", original)
