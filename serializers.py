from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Event, Registration


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class EventListSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    spots_left = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "location", "start_time", "end_time",
            "capacity", "organizer", "spots_left",
        ]

    def get_spots_left(self, obj):
        if obj.capacity == 0:
            return None  # unlimited
        return max(obj.capacity - obj.active_registration_count, 0)


class EventDetailSerializer(EventListSerializer):
    is_registered = serializers.SerializerMethodField()

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ["description", "is_full", "is_registered"]

    def get_is_registered(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.registrations.filter(user=user, status=Registration.Status.CONFIRMED).exists()


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "description", "location", "start_time", "end_time", "capacity"]
        read_only_fields = ["id"]

    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "event", "event_title", "user", "status", "registered_at", "cancelled_at"]
        read_only_fields = ["status", "registered_at", "cancelled_at"]
