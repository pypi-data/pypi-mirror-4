from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    FACEBOOK_APP_ID = settings.FACEBOOK_APP_ID
except AttributeError:
    raise ImproperlyConfigured("Facebook app_id missing. Set FACEBOOK_APP_ID in settings.py")

try:
    FACEBOOK_APP_SECRET = settings.FACEBOOK_APP_SECRET
except AttributeError:
    raise ImproperlyConfigured("Facebook app_secret missing. Set FACEBOOK_APP_SECRET in settings.py")

try:
    EVENTS_FQL = settings.FACEBOOK_EVENTS_FQL
except AttributeError:
    EVENTS_FQL = """
        SELECT name, pic, start_time, end_time, location, description
        FROM event WHERE eid IN ( SELECT eid FROM event_member WHERE uid = %s )
        ORDER BY start_time asc
    """
