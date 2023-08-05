# register priority/severity sorting stored procedures
from rql.utils import register_function, FunctionDescr


class priority_sort_value(FunctionDescr):
    supported_backends = ('postgres', 'sqlite',)
    rtype = 'Int'
class version_sort_value(FunctionDescr):
    supported_backends = ('postgres', 'sqlite',)
    rtype = 'Int'

try:
    register_function(priority_sort_value)
    register_function(version_sort_value)
except AssertionError:
    pass



try:
    from cubicweb.server import SQL_CONNECT_HOOKS
except ImportError: # no server installation
    pass
else:

    def init_sqlite_connexion(cnx):
        def _priority_sort_value(text):
            return {"minor": "2", "normal": "1", "important":  "0"}[text]
        cnx.create_function("PRIORITY_SORT_VALUE", 1, _priority_sort_value)

        def _version_sort_value(text):
            try:
                version, _sep, revision = text.partition('-')
                return sum([1000000,10000,100][i]*int(v) for i, v in enumerate(version.split("."))) + int(revision or 0)
            except (ValueError, IndexError, AttributeError):
                return 0
        cnx.create_function("VERSION_SORT_VALUE", 1, _version_sort_value)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault('sqlite', [])
    sqlite_hooks.append(init_sqlite_connexion)

# XML <-> yams equivalence
from cubicweb.xy import xy
xy.add_equivalence('Project', 'doap:Project')
xy.add_equivalence('Project creation_date', 'doap:Project doap:created')
