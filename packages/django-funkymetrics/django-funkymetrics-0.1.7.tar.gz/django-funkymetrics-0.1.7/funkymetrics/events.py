import urllib

from django.contrib.auth.models import User

from funkymetrics.tasks import send_event


def record_event(request_or_user, action, props=None):
    """
    Invokes a task to asynchronously record an event.
    """

    identity = ''
    user = request_or_user

    # If argument isn't a user, assume it's a request with a user.
    if not isinstance(request_or_user, User):
        user = request_or_user.user

    if user is not None and user.is_authenticated():

        # Identify by username
        identity = user.username

    else:

        # Attempt to identify by KISSmetrics ID from cookie
        if hasattr(request_or_user, 'COOKIES') is not None:
            identity = request_or_user.COOKIES.get('km_ai', '')

    # URL encode properties
    if props is not None:
        for key, val in props.items():
            props[key] = urllib.quote_plus(val)

    # Queue task
    if identity != '':
        send_event.delay(identity, action, props)
