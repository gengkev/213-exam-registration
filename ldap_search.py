import sys
import ldap3

from registration.models import *

ldap_server = 'ldap.andrew.cmu.edu'
server = ldap3.Server(ldap_server, use_ssl=True)
conn = ldap3.Connection(server, auto_bind=True)

all_users = User.objects.all()
for user in all_users:
    username = user.username
    #print('** processing', username)

    search_base = 'ou=person,dc=cmu,dc=edu'
    attributes = ['givenName', 'sn', 'cn', 'mail', 'cmuPersonAffiliation']
    #attributes = ldap3.ALL_ATTRIBUTES

    escaped_username = ldap3.utils.conv.escape_filter_chars(username)
    search_filter = '(cmuAndrewID={})'.format(escaped_username)

    conn.search(search_base, search_filter, attributes=attributes)
    if len(conn.entries) == 1:
        #print(conn.entries[0])
        #print('cn:', conn.entries[0].cn)
        #print('givenName:', conn.entries[0].givenName)
        #print('sn:', conn.entries[0].sn)
        #print('mail:', conn.entries[0].mail)

        first_name = (conn.entries[0].givenName)
        last_name = (conn.entries[0].sn)
        email = (conn.entries[0].mail)

        if len(first_name) != 1 or len(last_name) != 1 or len(email) != 1:
            print('** user {} has bad num entries'.format(username))
            print('   {} {} {}'.format(first_name, last_name, email))
            continue

        if (user.first_name, user.last_name, user.email) != \
                (first_name, last_name, email):

            print('** user {} differs:'.format(username))
            print('   first_name: {} {}'.format(user.first_name, first_name))
            print('   last_name: {} {}'.format(user.last_name, last_name))
            print('   email: {} {}'.format(user.email, email))

            user.first_name = conn.entries[0].givenName
            user.last_name = conn.entries[0].sn
            user.email = conn.entries[0].mail
            user.save()

    else:
        print('received {} entries for {}'.format(
            len(conn.entries), username))


conn.unbind()
