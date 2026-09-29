from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Registration
from .serializers import (
    EventDetailSerializer,
    EventListSerializer,
    EventWriteSerializer,
    RegistrationSerializer,
)


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Only the event's organizer (or an admin) may edit/delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or obj.organizer_id == request.user.id


class EventListCreateView(generics.ListCreateAPIView):
    """GET: list upcoming events. POST: create an event (authenticated organizers)."""

    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return EventWriteSerializer if self.request.method == "POST" else EventListSerializer

    def get_queryset(self):
        qs = Event.objects.all()
        upcoming_only = self.request.query_params.get("upcoming")
        if upcoming_only:
            qs = qs.filter(start_time__gte=timezone.now())
        return qs

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: event details. PUT/PATCH/DELETE: organizer or admin only."""

    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]

    def get_serializer_class(self):
        return EventWriteSerializer if self.request.method in ("PUT", "PATCH") else EventDetailSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class RegisterForEventView(APIView):
    """POST /events/<id>/register/ - register the current user for an event."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        existing = Registration.objects.filter(event=event, user=request.user).first()
        if existing and existing.status == Registration.Status.CONFIRMED:
            return Response({"error": "Already registered for this event."}, status=status.HTTP_400_BAD_REQUEST)

        if event.is_full:
            return Response({"error": "This event is full."}, status=status.HTTP_400_BAD_REQUEST)

        if existing:
            existing.status = Registration.Status.CONFIRMED
            existing.cancelled_at = None
            existing.save()
            reg = existing
        else:
            reg = Registration.objects.create(event=event, user=request.user)

        return Response(RegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)


class CancelRegistrationView(APIView):
    """POST /events/<id>/cancel/ - cancel the current user's registration."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        reg = Registration.objects.filter(
            event_id=pk, user=request.user, status=Registration.Status.CONFIRMED
        ).first()
        if not reg:
            return Response(
                {"error": "No active registration found for this event."},
                status=status.HTTP_404_NOT_FOUND,
            )
        reg.status = Registration.Status.CANCELLED
        reg.cancelled_at = timezone.now()
        reg.save()
        return Response(RegistrationSerializer(reg).data)


class MyRegistrationsView(generics.ListAPIView):
    """GET /my-registrations/ - list the current user's registrations."""

    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).select_related("event")
