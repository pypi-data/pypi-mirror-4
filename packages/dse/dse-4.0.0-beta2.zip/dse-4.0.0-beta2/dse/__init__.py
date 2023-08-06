import types
import logging

from django.db.models import AutoField
from django.db.models.loading import get_models
from django.conf import settings
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

class dse_value_parser(classmethod):
    """

    """

    def __init__(self, *args, **kw):
        """

        """
        func = args[0]
        func.is_dse_value_parser = True
        super(dse_value_parser, self).__init__(*args, **kw)

def get_value_parsers_from_class(klass):
    return [getattr(klass, name) for name, parser in klass.__dict__.items() if isinstance(parser, dse_value_parser)]

ITEM_LIMIT = 1000  # How many items to cache before forcing an executemany.
PARAMTOKEN = '%s'
PK_ID = 'id'  # default name of primary key field
CLEAN_HOUSE = True  # To avoid crashing the django-debug-toolbar,
                    # Thanks https://bitbucket.org/ringemup :-) !!
CACHE_CURSOR = False # Thx Andre Terra

# a mapping of different database adapters/drivers, needed to handle different
# quotations/escaping of sql fields, see the quote-method.
_DBNAME_MAP = {
    'psycopg2': 'postgres',
    'MySQLdb': 'mysql',
    'sqlite3': 'sqlite',
    'sqlite': 'sqlite',
    'pysqlite2': 'sqlite'
    }


def get_defaultvalue_for_field_from_model(model, field):
    """
    Get default value, if any, for a specified field in a specified model.
    """
    if hasattr(model._meta, "_field_name_cache"):
        field_defs = model._meta._field_name_cache
    else:
        field_defs = model._meta._fields()
    for f in field_defs:
        if field == f.name:            
            if hasattr(f.default, '__name__'):
                if f.default.__name__ == 'NOT_PROVIDED':
                    return None
            return f.default
    return None


class DseException(Exception):
    action = 'unknown'

    def __init__(self, exception, table, sql, params):

        self.table = table
        self.sql = sql
        self.params = params
        self.exception = exception

    def __str__(self):
        return "DseException.%sError on table %s.\nSQL: %s.\nNumber of params: %s.\nException: %s" % \
               (self.action, self.table, self.sql, len(self.params), self.exception)


class InsertManyException(DseException):
    action = 'Insert'


class UpdateManyException(DseException):
    action = 'UpdateMany'


class UpdateOneException(DseException):
    action = 'UpdateOne'

    def __str__(self):
        return "DseException.%sError on table %s.\nSQL: %s.\nParams: %s.\nException: %s" % \
               (self.action, self.table, '\n'.join(self.sql), self.params, self.exception)


class DeleteManyException(DseException):
    action = 'DeleteMany'


class PrimaryKeyMissingInInsertValues(BaseException):
    pass


class PrimaryKeyInInsertValues(BaseException):
    pass


class DSE(object):
    
    def __init__(self, model, item_limit=ITEM_LIMIT, paramtoken=PARAMTOKEN):
        self.model = model
        self.connection = connection
        self.cached_cursor = connection.cursor()
        self.item_limit = item_limit
        self.paramtoken = paramtoken
        self.tablename = model._meta.db_table
        self.object_name = model._meta.object_name
        self.debug = False
        self.sql_calls = 0
        self.records_processed = 0
        self.value_parsers = get_value_parsers_from_class(model)

        mod = self.cursor.connection.__class__.__module__.split('.', 1)[0]
        self.dbtype = _DBNAME_MAP.get(mod)
        if self.dbtype == 'postgres':
            self._quote = lambda x: '"%s"' % x
        else:
            self._quote = lambda x: '`%s`' % x

        self.pk = model._meta.pk.name
        self.pk_is_autofield = isinstance(model._meta.pk, AutoField)
        self.fields = self.get_fields()
        self.default_values = {}

        for key in self.fields:
            if key != self.pk:
                self.default_values[key] = get_defaultvalue_for_field_from_model(self.model, key)

        self.insert_sql = self._generate_insert_sql()
        self.update_sql = self._generate_update_sql()
        self.reset()

    def reset(self):
        self.item_counter = 0
        self.insert_items = []
        self.delete_items = []
        self.bulk_updates = {}
        self.update_items = []
        for field in self.fields:
            self.bulk_updates[field] = {}

    @property
    def cursor(self):
        """
        
        """
        if not CACHE_CURSOR:
            return connection.cursor()
        return self.cached_cursor
    
    def _generate_insert_sql(self):
        sql = 'insert into %s (%s) values (%s)' % (
            self._quote(self.tablename),
            ','.join(self._quote(f) for f in self.fields if f != self.pk or not self.pk_is_autofield),
            ','.join(self.paramtoken for f in self.fields if f != self.pk or not self.pk_is_autofield),
        )
        return sql
        
    def _generate_update_sql(self):
        sql = ['update %s set' % self._quote(self.tablename)]
        m = []
        for fieldname in self.fields:
            if fieldname == self.pk:
                continue
            m.append("%s = %s" % (self._quote(fieldname), self.paramtoken))
        sql.append(',\n'.join(m))
        sql.append('where %s = %s' % (self._quote(self.pk), self.paramtoken))
        return '\n'.join(sql)

    def _on_add(self):
        if self.item_counter >= self.item_limit:
            self.execute_sql()

    def get_fields(self):
        default_sql = 'select * from %s LIMIT 1' % self._quote(self.tablename)
        sql = {
               'sqlite': default_sql,
               'mysql': default_sql,
               'postgres': default_sql
               }
        cursor = connection.cursor()
        cursor.execute(sql.get(self.dbtype, 'select * from %s where 1=2' % self._quote(self.tablename)))
        fields = []
        for idx, field_attrs in enumerate(cursor.description):
            fields.append(field_attrs[0])
        self.clean_house()
        return fields

    def execute_insert_statements(self):
        "Executes all bulk insert statements."
        fieldvalues = []
        for items in self.insert_items:
            m = []
            for fieldname in self.fields:
                if fieldname in items:
                    m.append(items[fieldname])
                elif fieldname != self.pk or not self.pk_is_autofield:
                    m.append(None)
            fieldvalues.append(m)
            self.records_processed += 1
        if self.debug:
            logging.debug("Executing insert: %s" % self.insert_sql)
            for f in fieldvalues:
                logging.debug(str(f))
        try:
            self._execute(self.insert_sql, fieldvalues, many=True)
        except Exception as e:
            raise InsertManyException(e, self.tablename, self.insert_sql, fieldvalues)

    def execute_delete_statements(self):
        """
        Executes all bulk delete statements.
        """
        self.model.objects.filter(**{"%s__in" % self.pk: self.delete_items}).delete()
        self.records_processed += 1

    def execute_sql(self):
        """
        Executes all cached sql statements.
        """
        if self.bulk_updates:
            self.execute_bulk_updates()

        if self.update_items:
            self.execute_updates()

        if self.insert_items:
            self.execute_insert_statements()

        if self.delete_items:
            self.execute_delete_statements()

        self.reset()

    def _execute(self, sql, fieldvalues, many=True):
        self.sql_calls += 1
        try:
            if many:
                self.cursor.executemany(sql, fieldvalues)
            else:
                self.cursor.execute(sql, fieldvalues)
        except:
            self.cursor = self.connection.cursor()
            if many:
                self.cursor.executemany(sql, fieldvalues)
            else:
                self.cursor.execute(sql, fieldvalues)
        finally:
            self.clean_house()

    def execute_updates(self):
       params_for_executemany = []
       params_for_execute = []
       # If there all fields are present we can optimize and use executemany,
       # if not we must execute each SQL call in sequence
       for items in self.update_items:
           if len(items.keys()) != len(self.fields):
               params_for_execute.append(items)
           else:
               found_all_fields = True
               for field in self.fields:
                   if not field in items:
                       found_all_fields = False
                       break

               if found_all_fields:
                   params_for_executemany.append(items)
               else:
                   params_for_execute.append(items)

       if params_for_executemany:
           fieldvalues = []
           for items in params_for_executemany:
               m = []
               for fieldname in self.fields:
                   if fieldname == self.pk:
                       continue
                   if fieldname in items:
                       m.append(items[fieldname])
                   else:
                       m.append(None)
               m.append(items.get(self.pk))
               fieldvalues.append(m)
               self.records_processed += 1

           if self.debug:
               logging.debug("Executing update: %s" % self.update_sql)
               for f in fieldvalues:
                   logging.debug(str(f))

           try:
               self._execute(self.update_sql, fieldvalues, many=True)
           except Exception as e:
               raise UpdateManyException(e, self.tablename, self.update_sql, fieldvalues)

       for items in params_for_execute:
           sql = ['update %s set' % self._quote(self.tablename)]
           m = []
           fieldvalues = []
           for fieldname in items.keys():
               if fieldname == self.pk or fieldname not in self.fields:
                   continue
               m.append("%s = %s" % (self._quote(fieldname), self.paramtoken))
               fieldvalues.append(items[fieldname])
           sql.append(',\n'.join(m))
           sql.append('where %s = %s' % (self._quote(self.pk), self.paramtoken))
           fieldvalues.append(items[self.pk])
           self.records_processed += 1
           if self.debug:
               logging.debug("Executing update: %s" % '\n'.join(sql))
               for f in fieldvalues:
                   logging.debug(str(f))

           try:
               self._execute('\n'.join(sql), fieldvalues, many=False)
           except Exception as e:
               raise UpdateOneException(e, self.tablename, sql, fieldvalues)


    def execute_bulk_updates(self):
        "Executes the bulk bulk update statements"
        for field, values in self.bulk_updates.items():
            for value, ids in values.items():
                self.model.objects.filter(**{"%s__in" % self.pk: ids}).update(**{field: value})
                self.records_processed += 1

    def clean_house(self):
        """
        This method removes the last query from the list of queries stored in the django connection
        object. The django-debug-toolbar modifies that list and if we leave our dse based query lying around
        it will cause the debug-toolbar to crash.

        To disable this feature set dse.CLEAN_HOUSE = False.
        This method might later on be used for other things as well.
        """
        if CLEAN_HOUSE:
            if self.debug:
                logging.debug("DSE cleaning house: removing the last query from the list of queries in the connection object.")
            #if hasattr(self, 'connection'):
            #    if hasattr(self.connection, 'queries'):
            self.connection.queries = self.connection.queries[:-1]
        
    def flush(self):
        "Clears cache, executes cached sql statements."
        self.close()

    def close(self):
        "Clears cache, executes cached sql statements."
        self.execute_sql()

    def __exit__(self, type, value, traceback):
        "Calls close when exiting the with-block."
        self.close()

    def __enter__(self):
        "When using with SomeModel.delayed as d, d = self."
        return self

    def parse_values(self, values):
        "Executes any values parsers found in model."
        for parser in self.value_parsers:
            values = parser(values)
            if not values:
                return
        return values
        
    def update(self, values):
        "Adds a set of values to execute as update using cursor.executemany"
        if not self.pk in values:
            raise PrimaryKeyMissingInInsertValues(self.pk)
        
        values = self.parse_values(values)
        if not values:
            return
        
        self.update_items.append(values)
        self.item_counter += 1
        self._on_add()
    
    def bulk_update(self, values):
        "Adds a set of values to use for alternative bulk updates, using Model.objects.filter(id__in=...).update()"
        pk = values.get(self.pk, None)
        if not pk:
            raise PrimaryKeyMissingInInsertValues("Missing primary key. Required for call to prepare.")

        values = self.parse_values(values)
        if not values:
            return

        del values[self.pk]
        for k,v in values.items():
            self.bulk_updates.setdefault(k, {}).setdefault(v, []).append(pk)
        self.item_counter += 1
        self._on_add()

    def insert(self, values):
        "Adds a dictionary with values to insert/update"
        if self.pk in values and self.pk_is_autofield:
            raise PrimaryKeyInInsertValues(self.pk)

        final_values = {}
        for k, v in self.default_values.items():
            if callable(v):
                final_values[k] = v()
            else:
                final_values[k] = v

        final_values.update(values)
        
        final_values = self.parse_values(final_values)
        if not final_values:
            return

        self.insert_items.append(final_values)
        self.item_counter += 1
        self._on_add()

    def delete(self, pk):
        "Adds a primary key to the deletion queue."
        assert type(pk) == types.IntType, "pk argument must be integer."
        self.delete_items.append(pk)
        self.item_counter += 1
        self._on_add()


def patch_models(specific_models=None):
    """
    This method will monkey patch all models in installed apps to expose a dse attribute.
    Specific_models can be a list fo models to patch and when used only those models will be
    touched. Otherwise DSE patches every model it can find for all apps.
    """
    assert hasattr(settings, 'DATABASES') or hasattr(settings, 'DATABASE'), "Database information not found in settings."
    assert len(settings.DATABASES.keys()) > 0, "No database has been configured."
    # So far we only monkey-patch models if one database has been configured.
    if len(settings.DATABASES.keys()) != 1:
        logging.warning("DSE has not monkey-patched any models because more than one database has been configured.")
        return

    for model in get_models():
        #if not model._meta.managed:
        #    continue
        if specific_models and model not in specific_models:
            continue

        setattr(model, 'delayed', DSE(model, ITEM_LIMIT, PARAMTOKEN))
