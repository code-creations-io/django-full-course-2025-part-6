from django.utils import timezone
from django.db.models.signals import pre_save
from .models import LessonProgress
from django.dispatch import receiver

@receiver(pre_save, sender=LessonProgress)
def set_completed_at_for_progress(sender, instance, **kwargs):
    """
    Keep LessonProgress.completed_at in sync with completed.

    - If completed switches to True and completed_at is empty, set it to now.
    - If completed is False, clear completed_at.
    """
    if instance.completed:
        # If user has completed the lesson and no timestamp yet, set it
        if instance.completed_at is None:
            instance.completed_at = timezone.now()
    else:
        # If marked as not completed, clear the timestamp
        if instance.completed_at is not None:
            instance.completed_at = None