# Django Full Course 2025 — Part 5

## API Documentation with DRF & drf-spectacular

Welcome to **Part 5** of the Django Full Course 2025!  
In this section, you’ll add **beautiful, production‑ready API documentation** to your Django REST Framework project using **drf-spectacular** — the modern, officially recommended schema generator for DRF.

You’ll learn how to:

- Install and configure `drf-spectacular`
- Automatically generate an OpenAPI schema
- Create interactive Swagger and Redoc documentation
- Add custom metadata, tags, and component schemas
- Document custom actions and nested routes
- Expose schema endpoints for CI/CD and frontend teams

---

# 🚀 1. Install drf-spectacular

Run:

```bash
pip install drf-spectacular
```

Add it to `requirements.txt`:

```
drf-spectacular>=0.27.0
```

---

# ⚙️ 2. Add to `settings.py`

Update your REST framework configuration:

```python
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

Add the app:

```python
INSTALLED_APPS = [
    ...
    "drf_spectacular",
    "drf_spectacular_sidecar",  # optional: for offline Swagger UI assets
]
```

Add spectacular settings:

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "LMS API",
    "DESCRIPTION": "API documentation for the LMS platform used in this Django course.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
}
```

---

# 📡 3. Create API documentation routes

In `urls.py`:

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    ...
    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Interactive Swagger UI
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Interactive Redoc UI
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc-ui",
    ),
]
```

Visit:

- `http://localhost:8000/api/docs/swagger/`
- `http://localhost:8000/api/docs/redoc/`
- `http://localhost:8000/api/schema/`

---

# 🧩 4. Documenting Your Views Automatically

DRF + drf-spectacular automatically extracts schema information from:

- Viewsets
- Serializers
- Fields & Datatypes
- Permissions
- Pagination
- Filters
- Custom actions

Your Part 4 views will now appear automatically in the docs.

Example:

```python
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filterset_fields = ["module", "module__course"]
    search_fields = ["name", "slug", "content"]
    ordering_fields = ["order"]
```

This automatically generates:

- Endpoints for list/create/retrieve/update/delete
- Query params for filtering, searching & ordering
- Schema for request/response bodies

---

# ✨ 5. Adding Docs for Custom Actions

Custom actions appear automatically, but we can improve them.

Modify your `mark_complete` action:

```python
from drf_spectacular.utils import extend_schema

class LessonViewSet(viewsets.ModelViewSet):

    @extend_schema(
        description="Mark a lesson as complete for the authenticated user.",
        responses={200: dict(message=str)},
    )
    @action(detail=True, methods=["post"])
    def mark_complete(self, request, pk=None):
        return Response({"message": "Lesson marked complete"})
```

---

# 🏷️ 6. Add Tags to Organize Your Documentation

Group viewsets into tags:

```python
@extend_schema(tags=["Lessons"])
class LessonViewSet(viewsets.ModelViewSet):
    ...
```

Example for Courses:

```python
@extend_schema(tags=["Courses"])
class CourseViewSet(viewsets.ModelViewSet):
    ...
```

---

# 📘 7. Defining Custom Component Schemas

Useful when documenting reusable objects.

Example:

```python
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Simple Lesson",
            value={"id": 1, "name": "Intro", "content": "Welcome!"}
        )
    ]
)
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
```

---

# 🚦 8. Generating the Schema File for CI/CD

Generate a JSON/YAML schema locally:

```bash
python manage.py spectacular --file schema.yaml
```

Useful for:

- Frontend TypeScript clients
- API validation
- Contract testing

---

# 🧪 9. Using the Schema with API Clients (Bonus)

You can generate clients automatically using tools like:

- **openapi-typescript**
- **Swagger Codegen**
- **OpenAPI Generator**

Example:

```bash
npx openapi-typescript http://localhost:8000/api/schema/ -o api-types.ts
```

---

# 🎉 Final Result

By the end of Part 5, your Django API will have:

- Automatic OpenAPI schema
- Swagger UI documentation
- Redoc documentation
- Tag‑organized endpoints
- Documented custom actions
- Schema generators for dev teams

Your LMS API is now **discoverable**, **professional**, and ready for real‑world development workflows.

---

# ✅ Next Steps

In **Part 6**, we will explore:

- Signals!

Stay tuned!
