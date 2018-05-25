from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import PermissionDenied


class CustomRemoteUserBackend(RemoteUserBackend):
    # Suffix used for Andrew emails
    ANDREW_EMAIL_SUFFIX = '@andrew.cmu.edu'

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
        if username.endswith(self.ANDREW_EMAIL_SUFFIX):
            return username[:-len(self.ANDREW_EMAIL_SUFFIX)]

        raise PermissionDenied("Only andrew.cmu.edu users are permitted")


    def configure_user(self, user):
        """
        Configure user after creation by updating email address and
        password fields accordingly. Returns the updated user.
        """
        user.email = user.username + self.ANDREW_EMAIL_SUFFIX
        user.set_unusable_password()
        user.save()

        # TODO: use info from CMU LDAP.
        # https://github.com/ScottyLabs/directory-api/blob/master/server.js
