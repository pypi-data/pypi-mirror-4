from __future__ import with_statement

from os import path, walk

from blazeweb.hierarchy import findfile, FileNotFound
from compstack.sqlalchemy import db

class NotDirectoryExc(Exception):
    pass

def run_component_sql(component, target, use_dialect=False):
    ''' see docs for run_app_sql(): usage is the same, execpt for the `component`
        parameter which should be a string representing the name of the
        component.
    '''

    try:
        _run_dir_sql('%s:sql/%s' % (component, target))
        return
    except (FileNotFound, NotDirectoryExc):
        pass

    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name)
    else:
        relative_sql_path = 'sql/%s.sql' % (target)
    _run_file_sql('%s:%s'%(component,relative_sql_path))

def run_app_sql(target, use_dialect=False):
    ''' used to run SQL from files in an apps "sql" directory:

        For Example:

            run_app_sql('a_directory')

        will run files "<myapp>/sql/a_directory/*.sql

        You can control the dialect used by putting a line like the following at
        the very top of the file:

        -- dialect-require: sqlite

        or

        -- dialect-require: postgresql, mssql

        If the target is not a directory, then:

            run_app_sql('test_setup')

        will run the file "<myapp>/sql/test_setup.sql"

        But, you may also want the dialect taken into account:

            run_app_sql('test_setup', True)

        will run the files:

            # sqlite DB
            /sql/test_setup.sqlite.sql
            # postgres DB
            /sql/test_setup.pgsql.sql
            ...

        The dialect prefix used is the same as the sqlalchemy prefix.

        Any SQL file can contain multiple statements.  They should be seperated
        with the text "--statement-break".

    '''
    try:
        _run_dir_sql('sql/%s' % target)
        return
    except (FileNotFound, NotDirectoryExc):
        pass

    if use_dialect:
        relative_sql_path = 'sql/%s.%s.sql' % (target, db.engine.dialect.name )
    else:
        relative_sql_path = 'sql/%s.sql' % target

    _run_file_sql(relative_sql_path)

def _run_dir_sql(rel_path):
    for filename, sql_block in yield_blocks_from_dir(rel_path):
        _execute_sql_block(sql_block)

def _run_file_sql(relative_sql_path):
    full_path = findfile(relative_sql_path)
    with open(full_path, 'rb') as fh:
        sql_file_contents = fh.read()
    for sql_block in yield_sql_blocks(sql_file_contents):
        _execute_sql_block(sql_block)

def _execute_sql_block(sql):
    try:
        db.sess.execute(sql)
    except Exception:
        db.sess.rollback()
        raise

def yield_blocks_from_dir(rel_path):
    """
        yields blocks of SQL from sql files in a directory

        rel_path: a path relative to the app's root
    """
    dirpath = findfile(rel_path)
    if not path.isdir(dirpath):
        raise NotDirectoryExc('path found, but "%s" is not a directory' % rel_path)
    for dirname, _, filenames in walk(dirpath):
        filenames.sort()
        for filename in filenames:
            if not filename.endswith('.sql'):
                continue
            with open(path.join(dirname, filename), 'rb') as fh:
                sql_file_contents = fh.read()
            line1, _ = sql_file_contents.split('\n', 1)
            if 'dialect-require:' not in line1 or db.engine.dialect.name in line1:
                for sql_block in yield_sql_blocks(sql_file_contents):
                    yield filename, sql_block

def yield_sql_blocks(file_contents):
    for sql_block in file_contents.split('--statement-break'):
        sql_block = sql_block.strip()
        if sql_block:
            yield sql_block
