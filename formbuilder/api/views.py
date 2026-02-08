from __future__ import annotations

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CustomForm
from .serializers import FormSchemaSerializer


class FormSchemaView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    @extend_schema(responses=FormSchemaSerializer)
    def get(self, request, slug: str, *args, **kwargs):
        if not getattr(settings, "FORMBUILDER_API_ENABLED", False):
            raise Http404("Form builder API is disabled")

        custom_form = get_object_or_404(
            CustomForm,
            slug=slug,
            status=CustomForm.FormStatus.PUBLISHED,
        )
        serializer = FormSchemaSerializer(instance=custom_form.json_schema)
        return Response(serializer.data)
