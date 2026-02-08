from __future__ import annotations

from rest_framework import serializers


class FormSchemaSerializer(serializers.Serializer):
    """Pass-through serializer so DRF Response hooks remain consistent."""

    def to_representation(self, instance):
        return instance or {}
