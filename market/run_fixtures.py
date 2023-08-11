import os
import django
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

files = os.listdir("fixtures")
for i in files:
    call_command("loaddata", "fixtures/" + i)
