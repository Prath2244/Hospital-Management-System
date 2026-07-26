import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from django.contrib.sessions.models import Session

# Delete all sessions
Session.objects.all().delete()
print("✅ All sessions cleared! You will need to login again.")