from funkymetrics import tasks


def record_event(request, action, props=None):
    """
    Invokes a task to asynchronously record an event.
    """

    # Get user identifier
    if request.user.is_authenticated():
        identity = request.user.username
    else:
        identity = request.COOKIES.get('km_ai', '')

    # Queue task
    tasks.send_event.delay(identity, action, props)
