from __future__ import annotations

from django.urls import path

from .views import FormSchemaView

urlpatterns = [
    path("<slug:slug>/", FormSchemaView.as_view(), name="form-schema"),
]
