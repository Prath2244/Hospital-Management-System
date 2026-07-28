import os
import sys
from django.core.management.commands.runserver import Command as BaseRunserverCommand
from django.contrib.sessions.models import Session

class Command(BaseRunserverCommand):
    def handle(self, *args, **options):
        session_count = Session.objects.all().count()
        Session.objects.all().delete()
        print(f"✅ Cleared {session_count} sessions. All users logged out.")
        super().handle(*args, **options)