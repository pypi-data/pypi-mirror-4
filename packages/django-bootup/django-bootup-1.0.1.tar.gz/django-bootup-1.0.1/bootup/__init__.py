__version__ = '1.0.1'

from django.conf import settings
from django.db.models import signals
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app
from django.contrib.auth.models import User
from profiles import create_profile, delete_profile
from bootup import bootup

# disable syncdb from prompting you to create a superuser.
# we need a superuser, so we let bootup create it for us.
signals.post_syncdb.disconnect(
    create_superuser,
    sender=auth_app,
    dispatch_uid = "django.contrib.auth.management.create_superuser"
)

# bootstrap our project (site) after syncdb
signals.post_syncdb.connect(bootup)

# when a user is created and saved to db, a profile for that user is also created
if getattr(settings, 'AUTH_PROFILE_MODULE', False):
    # latch on user creation if flag is set
    if getattr(settings, 'BOOTUP_USER_PROFILE_AUTO_CREATE', False):
        signals.post_save.connect(create_profile, sender=User)

        # latch on user deletion flag if both (create & delete) are set
        if getattr(settings, 'BOOTUP_USER_PROFILE_AUTO_DELETE', False):
            signals.post_delete.connect(delete_profile, sender=User)


