# Feature 009: Pedagogical Alerts

**Status**: Implemented
**Backend**: alert_manager.py (complete), alert model + schemas + API endpoints exist

## Summary

Frontend alert display for parents. Shows pedagogical alerts with severity levels (INFO/WARNING/CRITICAL), Arabic messages, timestamps, and read/unread status.

## Files

- `frontend/src/views/parent/Alerts.vue` — Alert list view with severity color coding
- Router: `/parent/alerts` route added
