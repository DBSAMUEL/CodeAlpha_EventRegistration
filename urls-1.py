from django.urls import path

from . import views

urlpatterns = [
    path("events/", views.EventListCreateView.as_view(), name="event-list-create"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path("events/<int:pk>/register/", views.RegisterForEventView.as_view(), name="event-register"),
    path("events/<int:pk>/cancel/", views.CancelRegistrationView.as_view(), name="event-cancel"),
    path("my-registrations/", views.MyRegistrationsView.as_view(), name="my-registrations"),
]
