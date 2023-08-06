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
        def priority_sort_value(text):
            return {"minor": "2", "normal": "1", "important":  "0"}[text]
        cnx.create_function("PRIORITY_SORT_VALUE", 1, priority_sort_value)

        def version_sort_value(text):
            try:
                return sum((10000, 100, 1)[i]*int(v) for i, v in enumerate(text.split(".")))
            except (ValueError, IndexError, AttributeError):
                return 0
        cnx.create_function("VERSION_SORT_VALUE", 1, version_sort_value)

    sqlite_hooks = SQL_CONNECT_HOOKS.setdefault('sqlite', [])
    sqlite_hooks.append(init_sqlite_connexion)
