from django.conf import settings

def errors_to_abort_loader():
    return getattr(settings, 'ERRORS_TO_ABORT_LOADER', [])
