import sys
import ldap3

ldap_server = 'ldap.andrew.cmu.edu'
server = ldap3.Server(ldap_server, use_ssl=True)
conn = ldap3.Connection(server, auto_bind=True)

for username in sys.argv[1:]:
    print()
    print('** processing', username)

    search_base = 'ou=person,dc=cmu,dc=edu'
    attributes = ['givenName', 'sn', 'cn', 'mail']

    escaped_username = ldap3.utils.conv.escape_filter_chars(username)
    search_filter = '(cmuAndrewID={})'.format(escaped_username)

    conn.search(search_base, search_filter, attributes=attributes)
    if len(conn.entries) == 1:
        print('cn:', conn.entries[0].cn)
        print('givenName:', conn.entries[0].givenName)
        print('sn:', conn.entries[0].sn)
        print('mail:', conn.entries[0].mail)

    else:
        print('received', len(conn.entries), 'entries')

conn.unbind()
