# CodeAlpha_EventRegistration

Task 2 of the CodeAlpha Backend Development Internship: an Event Registration System built with **Django** and **Django REST Framework**.

## Features
- **Event model**: title, description, location, start/end time, capacity, organizer
- **Registration model**: links a user to an event, with `confirmed`/`cancelled` status, one active registration per user per event
- API endpoints to:
  - List events (`GET /api/events/`), optionally filtered to upcoming only (`?upcoming=1`)
  - View event details, including spots left and whether the current user is registered (`GET /api/events/<id>/`)
  - Create an event as an authenticated organizer (`POST /api/events/`)
  - Update/delete an event — organizer or admin only (`PUT`/`PATCH`/`DELETE /api/events/<id>/`)
  - Register for an event (`POST /api/events/<id>/register/`) — blocks duplicates and enforces capacity
  - Cancel a registration (`POST /api/events/<id>/cancel/`) — frees up a spot for others
  - View your own registrations (`GET /api/my-registrations/`)
- Django admin panel for organizers/staff to manage events and see registrations inline

## Run locally
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for the admin panel
python manage.py runserver
```
API base: http://127.0.0.1:8000/api/
Admin panel: http://127.0.0.1:8000/admin/

## Example usage
```bash
# Log in via Django's session auth (use a browser or DRF's browsable API at /api/events/)
# Create an event (must be authenticated)
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -b cookies.txt -d '{
    "title": "Django Workshop",
    "description": "Intro to Django",
    "location": "Room 101",
    "start_time": "2026-10-01T10:00:00Z",
    "end_time": "2026-10-01T12:00:00Z",
    "capacity": 50
  }'

# Register for an event
curl -X POST http://127.0.0.1:8000/api/events/1/register/ -b cookies.txt

# Cancel a registration
curl -X POST http://127.0.0.1:8000/api/events/1/cancel/ -b cookies.txt
```

## Notes
- Capacity of `0` means unlimited spots.
- Cancelling a registration frees the spot for someone else to register.
- Only the event's organizer (or an admin/staff user) can edit or delete that event.
