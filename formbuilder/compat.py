"""Compatibility shims to keep django-formbuilder stable across Python releases."""

from __future__ import annotations

from django.template.context import BaseContext, RequestContext


def _safe_basecontext_copy(self: BaseContext) -> BaseContext:
    """Simplified clone that avoids copying ``super()`` instances (Python 3.14 bug)."""
    # RequestContext requires a request argument, so we need to handle it specially
    if isinstance(self, RequestContext):
        duplicate = self.__class__(self.request)
        # Copy all internal state from the original context
        for attr in ["_processors_index", "template"]:
            if hasattr(self, attr):
                setattr(duplicate, attr, getattr(self, attr))
    else:
        duplicate = self.__class__()
    duplicate.dicts = list(self.dicts)
    return duplicate


def patch_template_context_copy() -> None:
    """Apply the safer implementation unconditionally to avoid AttributeError crashes."""
    BaseContext.__copy__ = _safe_basecontext_copy
