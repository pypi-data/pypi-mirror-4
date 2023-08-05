import os
from django.conf import settings
from django.core.management import call_command

# load up fixtures right after the last installed app is loaded up
def load_fixtures():
    """
    Load initial fixtures located @ BOOTUP_INITIAL_FIXTURES_DIRS defined in settings
    """
    path = getattr( settings, 'BOOTUP_INITIAL_FIXTURES_DIRS', "")
    if path and os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                call_command("loaddata", os.path.join(root, file))



