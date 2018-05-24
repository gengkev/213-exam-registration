from django.contrib.auth.backends import RemoteUserBackend

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
        if username.endswith(ANDREW_EMAIL_SUFFIX):
            return username[:-len(ANDREW_EMAIL_SUFFIX)]

        # TODO: figure out what to do with this
        raise ValueError("Email must end with @andrew.cmu.edu")


    def configure_user(user):
        """
        Configure user after creation by updating email address and
        password fields accordingly. Returns the updated user.
        """
        user.email = user.username + ANDREW_EMAIL_SUFFIX
        user.set_unusable_password()

        # TODO: use info from CMU LDAP.
        # https://github.com/ScottyLabs/directory-api/blob/master/server.js
