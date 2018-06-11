from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import PermissionDenied

from examreg import settings


class CustomRemoteUserBackend(RemoteUserBackend):
    # Let any Andrew ID log in and have a database entry created
    create_unknown_user = True


    def clean_username(self, username):
        """
        Clean the received REMOTE_USER value. For our setup, this is the
        email address that was authenticated through Shibboleth. We use
        Andrew IDs as usernames, so only accept Andrew emails.

        Returns the extracted Andrew ID, or raises a ValueError if the
        username was invalid.
        """
        # Extract Andrew ID
        if username.endswith(settings.ANDREW_EMAIL_SUFFIX):
            return username[:-len(settings.ANDREW_EMAIL_SUFFIX)]

        raise PermissionDenied(
            "Only andrew.cmu.edu identities are permitted"
        )


    def configure_user(self, user):
        """
        Configures a newly user that was created via remote user login.
        Returns the configured user.
        """
        user.configure_new()
        return user
