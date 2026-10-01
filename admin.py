from django.contrib import admin

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    readonly_fields = ["user", "status", "registered_at", "cancelled_at"]
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "location", "start_time", "capacity", "active_registration_count", "organizer"]
    list_filter = ["location", "start_time"]
    search_fields = ["title", "location"]
    inlines = [RegistrationInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "user", "status", "registered_at", "cancelled_at"]
    list_filter = ["status"]
    search_fields = ["user__username", "event__title"]
