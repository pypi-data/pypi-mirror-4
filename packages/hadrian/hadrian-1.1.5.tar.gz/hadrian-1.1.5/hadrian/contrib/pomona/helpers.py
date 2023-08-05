from hadrian.contrib.pomona.models import Log

def log_message(message, level="info"):
    Log.objects.create(level="Info", message=message)