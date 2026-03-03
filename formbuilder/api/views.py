from __future__ import annotations

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from ..models import CustomForm
from .serializers import FormSchemaSerializer


class FormSchemaView(APIView):
    # By default, authentication and permission classes are inherited from
    # DRF defaults (i.e. the host project's REST_FRAMEWORK settings).
    # Set FORMBUILDER_API_ANONYMOUS = True in Django settings to allow
    # unauthenticated access (restores pre-0.1.4 behavior).

    def get_authenticators(self):
        if getattr(settings, "FORMBUILDER_API_ANONYMOUS", False):
            return []
        return [auth() for auth in api_settings.DEFAULT_AUTHENTICATION_CLASSES]

    def get_permissions(self):
        if getattr(settings, "FORMBUILDER_API_ANONYMOUS", False):
            return []
        return [permission() for permission in api_settings.DEFAULT_PERMISSION_CLASSES]

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


