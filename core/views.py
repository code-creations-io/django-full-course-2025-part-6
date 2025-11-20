from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from core.models import Course, Module, Lesson, Enrollment, LessonProgress
from core.serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer,
    EnrollmentSerializer, LessonProgressSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = (
        Course.objects.select_related()
        .prefetch_related(
            "topics",
            "tags",
            "instructors",
            Prefetch("modules__lessons", queryset=Lesson.objects.only("id", "name", "slug", "order"))
        )
    )
    serializer_class = CourseSerializer

    filterset_fields = ["is_published", "tags", "topics"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Custom action: publish a course."""
        course = self.get_object()
        course.is_published = True
        course.save(update_fields=["is_published"])
        return Response({"status": "published"})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Custom action: list featured courses."""
        featured_courses = self.get_queryset().filter(is_published=True)
        page = self.paginate_queryset(featured_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(featured_courses, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related("course").prefetch_related("lessons")
    serializer_class = ModuleSerializer

    filterset_fields = ["course"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["order", "created_at", "updated_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = super().get_queryset()
        # If this is a nested route: /api/courses/<course_pk>/modules/
        course_pk = self.kwargs.get("course_pk")
        if course_pk:
            qs = qs.filter(course_id=course_pk)
        return qs

    def perform_create(self, serializer):
        # If nested, bind the FK from the URL; otherwise allow explicit course in body (optional)
        course_pk = self.kwargs.get("course_pk")
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            serializer.save(course=course)
        else:
            # Non-nested POST to /api/modules/ can still work if course provided
            serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("module", "module__course")
    serializer_class = LessonSerializer

    filterset_fields = ["module", "module__course"]
    search_fields = ["name", "slug", "content"]
    ordering_fields = ["order", "created_at", "updated_at"]
    ordering = ["order"]

    def get_queryset(self):
        qs = super().get_queryset()
        module_pk = self.kwargs.get("module_pk")
        if module_pk:
            qs = qs.filter(module_id=module_pk)
        return qs

    def perform_create(self, serializer):
        module_pk = self.kwargs.get("module_pk")
        if module_pk:
            module = get_object_or_404(Module, pk=module_pk)
            serializer.save(module=module)
        else:
            serializer.save()

    @action(detail=True, methods=["post"], url_path="mark-complete")  # optional, for hyphen URL
    def mark_complete(self, request, *args, **kwargs):
        """
        Custom action: mark a lesson as complete.
        Accept *args, **kwargs so nested router's module_pk doesn't break the signature.
        """
        lesson = self.get_object()  # respects get_queryset() filtering w/ module_pk
        # ⚠️ If LessonProgress.user is NOT nullable, don't pass user=None — it will 500.
        # For a public API, either make user nullable or gate this behind auth.
        LessonProgress.objects.update_or_create(
            user=None,  # only works if FK allows nulls; otherwise replace with request.user
            lesson=lesson,
            defaults={"completed": True},
        )
        return Response({"status": "completed"})