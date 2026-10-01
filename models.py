from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(
        default=0, help_text="Max registrations allowed. 0 means unlimited."
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time.")

    @property
    def active_registration_count(self):
        return self.registrations.filter(status=Registration.Status.CONFIRMED).count()

    @property
    def is_full(self):
        return self.capacity > 0 and self.active_registration_count >= self.capacity


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED)
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "user"], name="unique_event_user_registration")
        ]
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
