from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from core.views import CourseViewSet, ModuleViewSet, LessonViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"lessons", LessonViewSet, basename="lesson")

courses_router = NestedDefaultRouter(router, r"courses", lookup="course")
courses_router.register(r"modules", ModuleViewSet, basename="course-modules")

modules_router = NestedDefaultRouter(router, r"modules", lookup="module")
modules_router.register(r"lessons", LessonViewSet, basename="module-lessons")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include(courses_router.urls)),
    path("api/", include(modules_router.urls)),

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