from blazeutils import tolist
from savalidation import ValidationError
from sqlalchemy.exc import IntegrityError

from compstack.sqlalchemy import db

def sa_dialect_is(*testfor):
    for d in testfor:
        if db.engine.dialect.name == d:
            return True
    return False

def is_unique_exc(exc):
    if isinstance(exc, ValidationError):
        return len(exc.invalid_instances) == 1 and _is_unique_error_saval(exc.invalid_instances[0].validation_errors)
    if not isinstance(exc, IntegrityError):
        return False
    return _is_unique_msg(db.engine.dialect.name, str(exc))

def _is_unique_msg(dialect, msg):
    """
        easier unit testing this way
    """
    if dialect == 'postgresql':
        if 'duplicate key value violates unique constraint' in msg:
            return True
    elif dialect == 'mssql':
        if 'Cannot insert duplicate key' in msg:
            return True
    elif dialect == 'sqlite':
        if 'is not unique' in msg or 'are not unique' in msg:
            return True
    else:
        raise ValueError('is_unique_exc() does not yet support dialect: %s' % dialect)
    return False

def _is_unique_error_saval(validation_errors):
    if not len(validation_errors):
        return False
    for field, error_msgs in validation_errors.items():
        for err in tolist(error_msgs):
            if 'unique' not in err:
                return False
    return True

def is_fk_exc(exc, key_cname, ref_cname):
    """
        Use in testing to identify a FK constraint failure.

        Give then following column definition::

            [application_id] [int] NOT NULL REFERENCES [dbo].[auth_applications] ([id])

        Example usage of this function would be::

            try:
                # do something bad that violates the FK and commit
                ...
                dbsess.commit()
            except Exception, e:
                if not is_fk_exc(e, 'application_id', 'id'):
                    raise

        The params for this function are:

            key_cname = the name of the column that has the FK
            ref_cname = the name of the column (on a different table) that
                the FK references
    """
    if not isinstance(exc, IntegrityError):
        return False
    msg = str(exc).replace('(IntegrityError) ', '', 1)
    return _is_fk_msg(db.engine.dialect.name, msg, key_cname, ref_cname)

def _is_fk_msg(dialect, msg, key_cname, ref_cname):
    """
        easier unit testing this way
    """
    if dialect == 'sqlite':
        # this test assumes sqlite foreign keys created by SQLiteFKTG4SA.  The
        # reason the field name is in the msg is because SQLiteFKTG4SA uses
        # the field name as part of the constraint name
        if 'violates foreign key constraint' in msg and '__%s__fk' % key_cname in msg:
            return True
    elif dialect == 'postgresql':
        # postgresql does not have the field name in the message when the
        # record referenced by a FK is deleted, so don't check for field_name
        # here
        if 'violates foreign key constraint' in msg:
            if msg.startswith('insert or update') and ('Key (%s)=' % key_cname) in msg:
                return True
            if msg.startswith('update or delete') and ('Key (%s)=' % ref_cname) in msg:
                return True
    elif dialect == 'mssql':
        # this test assumes MSSQL 2005
        is_fk_message = 'conflicted with the FOREIGN KEY constraint' in msg
        is_ref_message = 'conflicted with the REFERENCE constraint' in msg
        # FK messages have the referenced column's info in them
        if is_fk_message and (r"column \'%s\'" % ref_cname) in msg:
                return True
        # FK messages have the key column's info in them
        if is_ref_message and (r"column \'%s\'" % key_cname) in msg:
            return True
    else:
        raise ValueError('is_fk_exc() does not yet support dialect: %s' % dialect)
    return False

def is_null_exc(exc, field_name):
    if isinstance(exc, ValidationError):
        if len(exc.invalid_instances) != 1:
            return False
        return _is_null_error_saval(exc.invalid_instances[0].validation_errors, field_name)
    if not isinstance(exc, IntegrityError):
        return False
    return _is_null_msg(db.engine.dialect.name, str(exc), field_name)

def _is_null_msg(dialect, msg, field_name):
    """
        easier unit testing this way
    """
    if dialect == 'mssql':
        if 'Cannot insert the value NULL into column \'%s\'' % field_name in msg:
            return True
    elif dialect == 'sqlite':
        if '.%s may not be NULL' % field_name in msg:
            return True
    elif dialect == 'postgresql':
        if 'null value in column "%s" violates not-null constraint' % field_name in msg:
            return True
    else:
        raise ValueError('is_null_exc() does not yet support dialect: %s' % dialect)
    return False

def _is_null_error_saval(validation_errors, field_name):
    if not len(validation_errors):
        return False
    for field, error_msgs in validation_errors.items():
        if field != field_name:
            return False
        for err in tolist(error_msgs):
            if 'Please enter a value' != err:
                return False
    return True

def is_check_const_exc(exc, constraint_name):
    if not isinstance(exc, IntegrityError):
        return False
    return _is_check_const(db.engine.dialect.name, str(exc), constraint_name)

def _is_check_const(dialect, msg, constraint_name):
    if dialect == 'mssql':
        if 'conflicted with the CHECK constraint' in msg and constraint_name in msg:
            return True
    elif dialect == 'sqlite':
        if 'constraint failed' in msg:
            return True
    elif dialect == 'postgresql':
        if 'violates check constraint' in msg and constraint_name in msg:
            return True
    else:
        raise ValueError('is_constraint_exc() does not yet support dialect: %s' % dialect)
    return False

def clear_db():
    if db.engine.dialect.name == 'postgresql':
        sql = []
        sql.append('DROP SCHEMA public cascade;')
        sql.append('CREATE SCHEMA public AUTHORIZATION %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO %s;' % db.engine.url.username)
        sql.append('GRANT ALL ON SCHEMA public TO public;')
        sql.append("COMMENT ON SCHEMA public IS 'standard public schema';")
        for exstr in sql:
            try:
                db.engine.execute(exstr)
            except Exception, e:
                print 'WARNING: %s' % e
    elif db.engine.dialect.name == 'sqlite':
        # drop the views
        sql = "select name from sqlite_master where type='view'"
        rows = db.engine.execute(sql)
        # need to get all views before start to try and delete them, otherwise
        # we will get "database locked" errors from sqlite
        records = rows.fetchall()
        for row in records:
            db.engine.execute('drop view %s' % row['name'])

        # drop the tables
        db.meta.reflect(bind=db.engine)
        for table in reversed(db.meta.sorted_tables):
            try:
                table.drop(db.engine)
            except Exception, e:
                if not 'no such table' in str(e):
                    raise
    elif db.engine.dialect.name == 'mssql':
        mapping = {
            'P': 'drop procedure [%(name)s]',
            'C': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            ('FN', 'IF', 'TF'): 'drop function [%(name)s]',
            'V': 'drop view [%(name)s]',
            'F': 'alter table [%(parent_name)s] drop constraint [%(name)s]',
            'U': 'drop table [%(name)s]',
        }
        delete_sql = []
        to_repeat_sql = []
        for type, drop_sql in mapping.iteritems():
            sql = 'select name, object_name( parent_object_id ) as parent_name '\
                'from sys.objects where type in (\'%s\')' % '", "'.join(type)
            rows = db.engine.execute(sql)
            for row in rows:
                delete_sql.append(drop_sql % dict(row))
        for sql in delete_sql:
            db.engine.execute(sql)
    else:
        return False
    return True

def clear_db_data():
    dialect_name = db.engine.dialect.name
    if dialect_name == 'postgresql':
        select_sql = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN('pg_catalog', 'information_schema')
            AND table_type = 'BASE TABLE'
        """
        truncate_sql = """
            TRUNCATE {0[table_schema]}.{0[table_name]} CASCADE
        """
        for row in db.sess.execute(select_sql):
            try:
                db.sess.execute(truncate_sql.format(row))
            except Exception, e:
                raise
                print 'WARNING: %s' % e
    elif dialect_name == 'sqlite':
       raise Exception('clear_db_data() does not yet support sqlite')
    elif dialect_name == 'mssql':
        raise Exception('clear_db_data() does not yet support mssql')
    else:
        raise Exception('clear_db_data() does not yet support {0}'.format(dialect_name))
    return True
