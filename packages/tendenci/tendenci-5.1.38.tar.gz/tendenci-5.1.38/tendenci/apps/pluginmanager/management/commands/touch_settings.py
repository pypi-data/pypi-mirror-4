import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from django.conf import settings
        settings_path = getattr(settings, "SETTINGS_PATH", None)
        if settings_path:
            os.system('touch ' + settings_path)
