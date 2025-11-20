# Django Full Course 2025 — Part 6

## Making Your App Event‑Driven with Django Signals

Welcome to **Part 6** of the Django Full Course 2025!

In this part, you’ll learn how to use **Django signals** to make your app _react_ automatically when important events happen — without scattering side‑effects all over your views and models.

We’ll cover:

- What signals are and when to use them
- How to create and connect signal receivers
- Automatically creating a profile when a user signs up
- Automatically updating lesson progress metadata when a lesson is completed
- How to organise signal code cleanly using `apps.py`
- How to test your signals in the Django shell and via the API

---

## 🧠 1. What Are Django Signals?

**Signals** let different parts of your app communicate with each other when certain events happen.

Examples:

- A `User` is created → automatically create a `Profile`
- A `LessonProgress` is marked complete → update progress metadata
- A `Course` is deleted → clean up related data

In this part, we’ll implement:

1. A **`post_save` signal** for `User` → auto‑create a `Profile`
2. A **`pre_save` signal** for `LessonProgress` → auto‑set `completed_at` and keep your progress data consistent

---

## ✅ 2. Prerequisites

This tutorial assumes you already have:

- A working Django project from previous parts
- Django REST Framework configured
- Models similar to:

```python
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="profiles/avatars/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


class Lesson(models.Model):
    name = models.CharField(max_length=255)
    # e.g. ForeignKey to Module, etc.
    # module = models.ForeignKey(Module, on_delete=models.CASCADE)
    # other fields...

    def __str__(self):
        return self.name


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{self.user} – {self.lesson} – completed={self.is_completed}"
```

> 🔎 Your actual project may have more fields, but the signal logic is the same.

---

## 🧩 3. Create a `signals.py` Module

Signals should live in a dedicated file so they’re easy to find and maintain.

In your app (for example: `core` or `accounts`), create a file:

**`core/signals.py`** (adjust the app name to match your project):

```python
# core/signals.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Profile, LessonProgress

User = get_user_model()
```

We’ll now add receivers step by step.

---

## 👤 4. Auto‑Create a Profile When a User is Created

We want:

- Every time a `User` is created → **also create a `Profile`**
- If the user is updated later → do nothing

Add this to `core/signals.py`:

```python
# core/signals.py (continued)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)
```

Optional: ensure a profile always exists (even if created manually later):

```python
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure the user's profile is saved whenever the User is saved.
    Useful if you add extra logic or default values to Profile.
    """
    if hasattr(instance, "profile"):
        instance.profile.save()
```

---

## 📚 5. Automatically Set `completed_at` for Lesson Progress

We want `LessonProgress` to behave like this:

- When `is_completed` becomes `True` and `completed_at` is empty → set `completed_at` to **now**
- If `is_completed` is `False` → clear `completed_at`
- This happens **before saving**, so we don’t need extra `save()` calls

Add a `pre_save` receiver to `core/signals.py`:

```python
from django.db.models.signals import pre_save

@receiver(pre_save, sender=LessonProgress)
def set_completed_at_for_progress(sender, instance, **kwargs):
    """
    Keep LessonProgress.completed_at in sync with is_completed.

    - If is_completed switches to True and completed_at is empty, set it to now.
    - If is_completed is False, clear completed_at.
    """
    if instance.is_completed:
        # If user has completed the lesson and no timestamp yet, set it
        if instance.completed_at is None:
            instance.completed_at = timezone.now()
    else:
        # If marked as not completed, clear the timestamp
        if instance.completed_at is not None:
            instance.completed_at = None
```

Now any time you create or update a `LessonProgress` row, the timestamp will be managed **automatically**.

---

## 🏗️ 6. Make Sure Signals Are Loaded (Using `apps.py`)

Django needs to import your `signals.py` file at startup.  
Best practice is to do this inside your app’s `AppConfig`.

### 6.1. Create/Update the AppConfig

Open or create `core/apps.py`:

```python
# core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
```

> 🔎 Replace `"core"` with your actual app name if different.

### 6.2. Register the AppConfig in `settings.py`

In `settings.py`, point Django to this config:

```python
INSTALLED_APPS = [
    # ...
    "core.apps.CoreConfig",
    # instead of just "core"
]
```

Now, every time Django starts, it will import `core.signals` and register your receivers.

---

## 🧪 7. Testing Signals in the Django Shell

Let’s verify everything works as expected.

### 7.1. Test User → Profile Creation

Run the shell:

```bash
python manage.py shell
```

Then:

```python
from django.contrib.auth import get_user_model
from core.models import Profile

User = get_user_model()

# Create a new user
user = User.objects.create_user(
    username="signal_test_user",
    email="signal@test.com",
    password="test1234",
)

# Check if a profile was created
Profile.objects.get(user=user)
```

If no exception is raised and you get a `Profile` object back, the signal is working. 🎉

You can also print it:

```python
profile = Profile.objects.get(user=user)
print(profile)
```

---

### 7.2. Test LessonProgress `completed_at` Logic

In the same shell (or a new one):

```python
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Lesson, LessonProgress

User = get_user_model()

user = User.objects.first()
lesson = Lesson.objects.first()

# 1. Create progress as not completed
progress = LessonProgress.objects.create(
    user=user,
    lesson=lesson,
    is_completed=False,
)

print(progress.is_completed)      # False
print(progress.completed_at)      # None

# 2. Mark as completed
progress.is_completed = True
progress.save()

progress.refresh_from_db()
print(progress.is_completed)      # True
print(progress.completed_at)      # Should now be set to a timestamp

# 3. Mark as not completed again
progress.is_completed = False
progress.save()

progress.refresh_from_db()
print(progress.is_completed)      # False
print(progress.completed_at)      # Should now be None again
```

If these printouts match the comments, your signal is working exactly as intended. ✅

---

## 🌐 8. Testing Signals Through the API

Because your `LessonProgress` is probably exposed via DRF viewsets (from Part 4):

1. Make sure you have an authenticated user (Session or Token)
2. Use a tool like **Postman**, **Insomnia**, or the DRF web UI at `/api/`
3. Hit the `LessonProgress` endpoint:

### 8.1. Create a Progress Record (not completed)

`POST /api/lesson-progress/`

```json
{
  "lesson": 1,
  "is_completed": false
}
```

Expected response:

- `is_completed`: `false`
- `completed_at`: `null`

### 8.2. Update Progress to Completed

`PATCH /api/lesson-progress/1/`

```json
{
  "is_completed": true
}
```

Expected response:

- `is_completed`: `true`
- `completed_at`: a timestamp string, e.g. `"2025-11-20T10:30:00Z"`

All of this happens **because of the signal**, not manual logic in your views or serializers.

---

## 🧹 9. When _Not_ to Use Signals

Signals are powerful, but they can also hide important logic if overused.

Avoid signals when:

- The logic is purely request‑specific and belongs in the view
- You need explicit control and testability
- The side‑effect is part of a clear workflow that other developers expect to see in the view/service layer

Good use cases for signals:

- Cross‑cutting concerns (profiles, audit logs, timestamps)
- Background bookkeeping (counters, cache invalidation)
- One‑off side‑effects where tight coupling would be messy

---

## 🎉 Final Result

By the end of **Part 6**, your project can:

- **Automatically create profiles** as users sign up
- **Automatically manage lesson completion timestamps**
- Keep side‑effects out of your views and serializers
- Organise signal logic cleanly with `apps.py` and `signals.py`

Your Django app is now **more event‑driven, maintainable, and scalable**.

---

## ⏭️ What’s Next?

In **Part 7** (optional), you might explore:

- Background tasks with Celery / RQ
- Email notifications on events
- Webhooks and outbound event streams
- Advanced auditing and logging

For now, your LMS is officially **reactive** — it responds automatically when the data changes, without extra boilerplate in your views. 🚀
