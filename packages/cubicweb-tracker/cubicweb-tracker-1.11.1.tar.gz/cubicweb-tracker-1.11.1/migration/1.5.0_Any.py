sync_schema_props_perms(('Ticket', 'type', 'String'))
rql('SET T type "enhancement" WHERE T is Ticket, T type "story"')
commit()
