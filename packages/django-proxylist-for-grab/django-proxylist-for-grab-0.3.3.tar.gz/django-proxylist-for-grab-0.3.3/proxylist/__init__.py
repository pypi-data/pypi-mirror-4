from datetime import datetime


def now():
    now = datetime.now
    try:
        from django.utils.timezone import now
    except ImportError:
        pass
    return now()
