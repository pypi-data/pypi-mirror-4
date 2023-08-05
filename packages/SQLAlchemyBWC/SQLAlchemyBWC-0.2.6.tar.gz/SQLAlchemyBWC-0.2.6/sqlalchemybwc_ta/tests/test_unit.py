from blazeutils.testing import raises
from nose.tools import eq_
import sqlalchemy.sql as sasql
from sqlalchemybwc import db
from sqlalchemybwc.lib.decorators import one_to_none_ncm, \
    assert_raises_null_or_fk_exc, assert_raises_null_exc, assert_raises_fk_exc
from sqlalchemybwc.lib.helpers import is_unique_exc, _is_unique_msg, \
    _is_unique_error_saval, _is_null_msg, _is_fk_msg, _is_check_const
from sqlalchemybwc.lib.sql import run_app_sql, run_component_sql
from sqlalchemybwc.lib.testing import query_to_str

from sqlalchemybwc_ta.model.orm import UniqueRecord, OneToNone, Car, \
    UniqueRecordTwo, Truck, CustomerType, NoDefaults, declarative_base
from sqlalchemybwc_ta.model.entities import Blog, Comment

def test_ignore_unique():
    assert UniqueRecord.add(u'test_ignore_unique')

    # unique exception should be ignore with iu version
    assert not UniqueRecord.add_iu(u'test_ignore_unique')

    # transaction should have been rolled back so we can add something else
    # without getting errors
    assert UniqueRecord.add(u'test_ignore_unique_ok')

    # should fail if we don't use the ignore unique (ui) method
    try:
        UniqueRecord.add(u'test_ignore_unique')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

    # transaction should have been rolled back so we can add something else
    # without getting errors
    assert UniqueRecord.add(u'test_ignore_unique_ok2')

def test_ignore_unique_two():
    assert UniqueRecordTwo.add(name=u'test_ignore_unique_two', email=u'tiu@example.com')

    # unique exception should be ignore with iu version
    assert not UniqueRecordTwo.add_iu(name=u'test_ignore_unique_two', email=u'tiu@example.com')

    # should fail if we don't use the ignore unique (ui) method
    try:
        UniqueRecordTwo.add(name=u'test_ignore_unique_two', email=u'tiu@example.com')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

def test_ignore_unique_indexes():
    assert Truck.add(u'ford', u'windstar')

    # unique exception should be ignore with iu version
    assert not Truck.add_iu(u'ford', u'windstar')

    # should fail if we don't use the ignore unique (ui) method
    try:
        Truck.add(u'ford', u'windstar')
        assert False
    except Exception, e:
        if not is_unique_exc(e):
            raise

def test_transaction_decorator():
    ur = UniqueRecord.add(u'test_transaction_decorator')
    assert ur.name == u'test_transaction_decorator'
    urid = ur.id
    db.sess.remove()
    ur = UniqueRecord.get(urid)
    assert ur.name == u'test_transaction_decorator'

def test_one_to_none_ncm():
    a = OneToNone.add(u'a')
    b1 = OneToNone.add(u'b')
    b2 = OneToNone.add(u'b')

    @one_to_none_ncm
    def hasone():
        return db.sess.query(OneToNone).filter_by(ident=u'a').one()

    @one_to_none_ncm
    def hasnone():
        return db.sess.query(OneToNone).filter_by(ident=u'c').one()

    @one_to_none_ncm
    def hasmany():
        return db.sess.query(OneToNone).filter_by(ident=u'b').one()

    assert a is hasone()
    assert hasnone() is None
    try:
        hasmany()
        assert False, 'expected exception'
    except Exception, e:
        if 'Multiple rows were found for one()' != str(e):
            raise

def test_declarative_stuff():
    c = Car.add(make=u'ford', model=u'windstar', year=u'1998')
    cd = c.to_dict()

    keys = cd.keys()
    assert cd['make'] == u'ford'
    assert cd['model'] == u'windstar'
    assert cd['year'] == 1998
    assert cd['createdts'] is not None
    assert cd['id'] > 0
    assert cd['updatedts'] is None

    c.year = 1999
    db.sess.commit()

    assert c.updatedts is not None

def test_from_dict():
    c = Car()
    c.from_dict({
        'make': u'chevy',
        'model': u'cav',
        'year': 1993
    })
    db.sess.add(c)
    db.sess.commit()
    cid = c.id
    assert cid
    db.sess.remove()
    c = Car.get(cid)
    assert c.make == 'chevy'

def test_get_by_and_where():
    Car.delete_all()
    Car.add(**{
        'make': u'chevy',
        'model': u'astro',
        'year': 1993
    })
    c = Car.get_by(make=u'chevy', model=u'astro', year=1993)
    assert c.model == 'astro'

    c = Car.get_where(Car.make == u'chevy', Car.year < 2000)
    assert c.model == 'astro'

    c = Car.get_where(Car.make == u'chevy', Car.year > 2000)
    assert c is None

def test_is_unique_msg():
    totest = {
        'sqlite': [
            "(IntegrityError) column name is not unique u'INSERT INTO sabwp_unique_records (name, updatedts) VALUES (?, ?)' (u'test_ignore_unique', None)"
        ],
        'postgresql':[
            """(IntegrityError) duplicate key value violates unique constraint "sabwp_unique_records_name_key" 'INSERT INTO sabwp_unique_records (name, updatedts) VALUES (%(name)s, %(updatedts)s) RETURNING sabwp_unique_records.id' {'updatedts': None, 'name': u'test_ignore_unique'}"""
        ],
        'mssql': [
            """(IntegrityError) ('23000', "[23000] [Microsoft][ODBC SQL Server Driver][SQL Server]Cannot insert duplicate key row in object 'dbo.auth_group' with unique index 'ix_auth_group_name'. (2601) (SQLExecDirectW)")""",
            """(IntegrityError) ('23000', "[23000] [Microsoft][ODBC SQL Server Driver][SQL Server]Violation of UNIQUE KEY constraint 'uc_auth_users_login_id'. Cannot insert duplicate key in object 'dbo.auth_user'. (2627) (SQLExecDirectW)") """
        ]
    }
    def dotest(dialect, msg):
        assert _is_unique_msg(dialect, msg)
    for k,v in totest.iteritems():
        for msg in v:
            yield dotest, k, msg

def test_is_null_msg():
    totest = {
        'sqlite': [
            "(IntegrityError) permissions.name may not be NULL u'INSERT INTO permissions..."
        ],
        'postgresql':[
            '(IntegrityError) null value in column "name" violates not-null constraint...'
        ],
        'mssql': [
            #"""The INSERT statement conflicted with the FOREIGN KEY constraint "fk_some_constraint_name". The conflict occurred in database "TestDB", table "dbo.permissions", column 'name'.""",
            """Cannot insert the value NULL into column 'name', table 'TestDB.dbo.permissions'; column does not allow nulls. INSERT fails.""",
            """Cannot insert the value NULL into column 'name', table 'TestDB.dbo.permissions'; column does not allow nulls. UPDATE fails.""",

        ]
    }
    def dotest(dialect, msg):
        assert _is_null_msg(dialect, msg, u'name')
    for k,v in totest.iteritems():
        for msg in v:
            yield dotest, k, msg

def test_is_fk_msg():
    totest = {
        # sqlite examples are from errors created by SQLiteFKTG4SA triggers
        'sqlite': [
            # prevent insert
            (True, 'insert on table "comments" violates foreign key constraint "comments__blog_ident__fki__blogs__ident__auto"'),
            # prevent update
            (True, 'update on table "comments" violates foreign key constraint "comments__blog_ident__fku__blogs__ident__auto"'),
            # prevent parent delete
            (True, 'delete on table "blogs" violates foreign key constraint "comments__blog_ident__fkd__blogs__ident__auto"'),
            # some other field
            (False, 'insert on table "comments" violates foreign key constraint "comments__user_id__fki__users__id__auto"'),
        ],
        'postgresql':[
            # preventing insert
            (True, """insert or update on table "comments" violates foreign key constraint "comments_blog_ident_fkey" DETAIL:  Key (blog_ident)=(10000) is not present in table "blogs"."""),
            # preventing update
            (True, """insert or update on table "comments" violates foreign key constraint "comments_blog_ident_fkey" DETAIL:  Key (blog_ident)=(10000) is not present in table "blogs"."""),
            # preventing parent update
            (True, """update or delete on table "blogs" violates foreign key constraint "comments_blog_ident_fkey" on table "comments" DETAIL:  Key (ident)=(EfCY15xOQocd) is still referenced from table "comments".)"""),
            # preventing parent delete
            (True, """update or delete on table "blogs" violates foreign key constraint "comments_blog_ident_fkey" on table "comments DETAIL:  Key (ident)=(hWYr3uG4ZAXU) is still referenced from table "comments"."""),
            # some other field than the one we are expecting
            (False, """insert or update on table "comments" violates foreign key constraint "comments_user_id_fkey" DETAIL:  Key (user_id)=(10000) is not present in table "users"."""),
        ],
        'mssql': [
            # preventing insert
            (True, r"""The INSERT statement conflicted with the FOREIGN KEY constraint "FK__comments__blog_i__4E88ABD4". The conflict occurred in database "temp", table "dbo.blogs", column \'ident\'."""),
            # preventing update
            (True, r"""The UPDATE statement conflicted with the FOREIGN KEY constraint "FK__comments__blog_i__4E88ABD4". The conflict occurred in database "temp", table "dbo.blogs", column \'ident\'."""),
            # preventing parent update
            (True, r"""The UPDATE statement conflicted with the REFERENCE constraint "FK__comments__blog_i__4E88ABD4". The conflict occurred in database "temp", table "dbo.comments", column \'blog_ident\'."""),
            # preventing parent delete
            (True, r"""The DELETE statement conflicted with the REFERENCE constraint "FK__comments__blog_i__4E88ABD4". The conflict occurred in database "temp", table "dbo.comments", column \'blog_ident\'."""),
            # some other field than the one we are expecting
            (False, r"""The INSERT statement conflicted with the FOREIGN KEY constraint "FK__comments__user_i__4E88ABDC4". The conflict occurred in database "temp", table "dbo.users", column \'id\'."""),
        ]
    }
    def test_is_fk(dialect, msg, is_fk_flag):
        retval = _is_fk_msg(dialect, msg, 'blog_ident', 'ident' )
        eq_(is_fk_flag, retval)

    for k,v in totest.iteritems():
        for is_fk_flag, msg in v:
            yield test_is_fk, k, msg, is_fk_flag

def test_is_check_constraint_msg():
    totest = {
        'sqlite': [
            (True, 'constraint failed'),
        ],
        'postgresql':[
            (True, 'new row for relation "auth_users" violates check constraint "ck_auth_users_uids_not_null"'),
            # some other constraint than the one we are expecting
            (False, 'new row for relation "auth_users" violates check constraint "ck_something_else"'),
        ],
        'mssql': [
            (True, 'The INSERT statement conflicted with the CHECK constraint "ck_auth_users_uids_not_null". The conflict occurred in database "testdb", table "dbo.auth_users"'),
            (False, 'The INSERT statement conflicted with the CHECK constraint "ck_something_else". The conflict occurred in database "testdb", table "dbo.auth_users"'),
        ]
    }
    def check_func(dialect, msg, expect):
        retval = _is_check_const(dialect, msg, 'ck_auth_users_uids_not_null' )
        eq_(expect, retval)

    for k,v in totest.iteritems():
        for expect, msg in v:
            yield check_func, k, msg, expect

def test_is_unique_error_saval():
    totest = [
        ({}, False),
        ({'label': 'not unique'}, True),
        ({'label': 'max size exceeded'}, False),
        ({'label': 'max size exceeded', 'name': 'not unique'}, False),
        ({'label': 'not unique', 'name': 'not unique'}, True),
        ({'label': ['max size exceeded', 'not unique']}, False),
    ]
    def dotest(validation_errors, return_val):
        assert _is_unique_error_saval(validation_errors) == return_val, 'expected %s for %s' % (return_val, validation_errors)
    for test_case in totest:
        yield dotest, test_case[0], test_case[1]

def test_delete():
    c = Car.add(**{
        'make': u'chevy',
        'model': u'astro',
        'year': 1993
    })
    cid = c.id
    assert Car.delete(cid)
    assert not Car.delete(cid)

def test_count_and_delete_all():
    Car.delete_all()
    c = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2010
    })
    c = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2009
    })
    c = Car.add(**{
        'make': u'test',
        'model': u'count2',
        'year': 2010
    })
    assert Car.count() == 3
    assert Car.count_by(model=u'count') == 2
    assert Car.count_where(Car.model == u'count') == 2
    eq_(Car.delete_all(), 3)

def test_query_attribute():
    Car.delete_all()
    c = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2010
    })
    assert Car.query().count() == 1

    # default usage should return all attributes
    c = Car.query().first()
    assert isinstance(c, Car)
    assert c.id
    assert c.make
    assert c.model

    # sending attribute names should give us a recordset with just those
    # attributes
    res = Car.query('id', 'make').first()
    assert not isinstance(res, Car)
    assert res.id
    assert res.make
    try:
        assert res.model
        assert False, 'expected exception'
    except AttributeError:
        pass

def test_delete_where():
    Car.delete_all()
    c = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2010
    })
    c = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2009
    })
    c = Car.add(**{
        'make': u'test',
        'model': u'count2',
        'year': 2010
    })

    # two clauses
    assert Car.delete_where(Car.model == u'count', Car.year == 2009) == 1
    assert Car.count() == 2

    # one clause
    assert Car.delete_where(Car.model == u'count2') == 1

def test_lists_pairs_firsts():
    Car.delete_all()
    c1 = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2008
    })
    c2 = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2009
    })
    c3 = Car.add(**{
        'make': u'test',
        'model': u'count2',
        'year': 2010
    })

    result = Car.list()
    assert len(result) == 3
    assert result[2] is c3

    result = Car.list_by(model=u'count2')
    assert len(result) == 1
    assert result[0] is c3

    result = Car.list_where(Car.model == u'count2')
    assert len(result) == 1
    assert result[0] is c3

    # with order_by clauses
    result = Car.list(order_by=Car.year.desc())
    assert result[2] is c1

    # multiple values for order_by
    result = Car.list(order_by=(Car.model, Car.year.desc()))
    assert result[0] is c2, result

    # with order by
    result = Car.list_by(model=u'count', order_by=Car.year.desc())
    assert result[0] is c2

    # with order by
    result = Car.list_where(Car.model == u'count', order_by=Car.year.desc())
    assert result[0] is c2

    #with extra arg
    try:
        Car.list_where(Car.model == u'count', order_by=Car.year.desc(), erroneous='foo')
        assert False
    except ValueError:
        pass

    ###
    ### test pairs
    ###
    expect = [
        (c1.id, c1.year),
        (c2.id, c2.year),
        (c3.id, c3.year),
    ]
    result = Car.pairs('id:year')
    eq_(expect, result)

    expect = [
        (c1.model, c1.year),
        (c2.model, c2.year),
        (c3.model, c3.year),
    ]
    result = Car.pairs('model:year')
    eq_(expect, result)

    expect = [
        (c3.model, c3.year),
        (c2.model, c2.year),
        (c1.model, c1.year),
    ]
    result = Car.pairs('model:year', order_by=Car.year.desc())
    eq_(expect, result)


    expect = [
        (c2.model, c2.year),
        (c1.model, c1.year),
    ]
    result = Car.pairs_by('model:year', model=u'count', order_by=Car.year.desc())
    eq_(expect, result)

    result = Car.pairs_where('model:year', Car.model == u'count', order_by=Car.year.desc())
    eq_(expect, result)

    result = Car.pairs_where('model:year', Car.model == u'we-need-an-empty-list', order_by=Car.year.desc())
    eq_([], result)

    ###
    ### test firsts
    ###
    c = Car.first()
    assert c is c1

    c = Car.first(order_by=Car.year.desc())
    assert c is c3

    c = Car.first_by(model=u'count2')
    assert c is c3

    c = Car.first_by(model=u'count', order_by=Car.year.desc())
    assert c is c2

    c = Car.first_where(Car.model == u'count2')
    assert c is c3

    c = Car.first_where(Car.model == u'count', order_by=Car.year.desc())
    assert c is c2

    c = Car.first_by(model=u'nothere')
    assert c is None

    try:
        c = Car.first_where(Car.model == u'count2', erronous='foo')
    except ValueError:
        pass

def test_edit():
    Car.delete_all()
    c1 = Car.add(**{
        'make': u'test',
        'model': u'count',
        'year': 2008
    })
    cid = c1.id
    Car.edit(c1.id, make=u'ford', year=2010)
    db.sess.remove()
    c = Car.first()
    assert c.make == 'ford'
    assert c.model == 'count'
    assert c.year == 2010
    c1 = Car.edit(year=2011, id=cid)
    assert c.make == 'ford'
    assert c.model == 'count'
    assert c.year == 2011

    try:
        c1 = Car.edit(year=2011)
        assert False
    except ValueError:
        pass

def test_update():
    Car.delete_all()
    c = Car.update(make=u'ford', year=2010, model=u'test')
    assert Car.count() == 1
    Car.update(c.id, year=2011)
    assert Car.count() == 1
    assert c.year == 2011

def test_lookup_object():
    CT = CustomerType
    c1 = CT.add(label=u'one')
    c2 = CT.testing_create(u'two')
    c3 = CT.testing_create(u'three', False)

    eq_([c2, c1], CT.list_active(order_by=CT.id.desc()))
    eq_([c1, c2], CT.list_active())
    assert [c1, c3, c2] == CT.list_active(c3.id)

    expect = [
        (c2.id, u'two'),
        (c1.id, u'one'),
    ]
    assert expect == CT.pairs_active(order_by=CT.id.desc())

    expect = [
        (c1.id, u'one'),
        (c2.id, u'two'),
    ]
    eq_(expect, CT.pairs_active())

    expect = [
        (c1.id, u'one'),
        (c3.id, u'three'),
        (c2.id, u'two'),
    ]
    assert expect == CT.pairs_active(c3.id)

    # test unique
    assert not CT.add_iu(label=u'one')

def test_sa_column_names():
    eq_(CustomerType.sa_column_names(), ['id', 'createdts', 'updatedts', 'active_flag', 'label'])
    eq_(Truck.sa_column_names(), ['id', 'createdts', 'updatedts', 'make', 'model'])

def test_no_default_columns():
    eq_(NoDefaults.sa_column_names(), ['myid', 'name'])

def test_declarative_base():
    Base1 = declarative_base()
    Base2 = declarative_base()
    assert Base1 is Base2

class TestSQLRunFuncs(object):

    def setUp(self):
        Truck.delete_all()

    def test_app_file(self):
        run_app_sql('run_sql_test1')
        eq_(Truck.count(), 3)

    def test_comp_file(self):
        run_component_sql('foo', 'run_sql_test1')
        eq_(Truck.count(), 3)

    def test_app_file_with_dialect(self):
        run_app_sql('run_sql_test1', use_dialect=True)
        eq_(Truck.count(), 2)

    def test_app_directory(self):
        run_app_sql('run_dir_test')
        eq_(Truck.count(), 2)
        trucks = Truck.list()
        # make sure the updates ran, this ensures the files are getting executed
        # in the correct order
        eq_(trucks[0].make, 'ford')
        eq_(trucks[0].model, 'f250')
        eq_(trucks[1].model, '2500')

    def test_app_directory_dialects(self):
        run_app_sql('run_dir_dialect_test')
        eq_(Truck.count(), 1)
        t = Truck.first()
        eq_(t.make, 'dialect')
        eq_(t.model, db.engine.dialect.name)

    def test_comp_dir(self):
        run_component_sql('foo', 'run_dir_test')
        eq_(Truck.count(), 2)
        trucks = Truck.list()

class TestAssertRaisesDecorators(object):

    def setUp(self):
        Comment.delete_all()
        Blog.delete_all()

    @assert_raises_null_or_fk_exc('name', 'n/a')
    def test_ARNFKE_with_null_exc(self):
        UniqueRecord.add(name=None)

    @assert_raises_null_exc('name')
    def test_ARNE_with_null_exc2(self):
        UniqueRecord.add(name=None)

    @raises(ValueError, 'passthru')
    def test_ARNE_exc_passthrough(self):
        @assert_raises_null_exc('n/a')
        def inner():
            raise ValueError('passthru')
        inner()

    @raises(ValueError, 'passthru')
    def test_ARNFKE_exc_passthrough(self):
        @assert_raises_null_or_fk_exc('n/a', 'n/a')
        def inner():
            raise ValueError('passthru')
        inner()

    @raises(ValueError, 'passthru')
    def test_ARFKE_exc_passthrough(self):
        @assert_raises_fk_exc('n/a', 'n/a')
        def inner():
            raise ValueError('passthru')
        inner()

    @raises(AssertionError, 'expected null exception to be raised')
    def test_ARNE_exc_expected(self):
        @assert_raises_null_exc('n/a')
        def inner():
            pass
        inner()

    @raises(AssertionError, 'expected null or FK exception to be raised')
    def test_ARNFKE_exc_expected(self):
        @assert_raises_null_or_fk_exc('n/a', 'n/a')
        def inner():
            pass
        inner()

    @raises(AssertionError, 'expected FK exception to be raised')
    def test_ARFKE_exc_expected(self):
        @assert_raises_fk_exc('n/a', 'n/a')
        def inner():
            pass
        inner()

    @assert_raises_null_or_fk_exc('blog_ident', 'ident')
    def test_ARNFKE_with_either_exc(self):
        # this test will generate the FK exception for SQLite
        # but a NULL exception for other DBs
        Comment.add(blog_ident=None)

    @assert_raises_null_or_fk_exc('blog_ident', 'ident')
    def test_ARNFKE_with_fk_exc(self):
        Comment.add(blog_ident='abcdefg')

    @assert_raises_fk_exc('blog_ident', 'ident')
    def test_ARFKE(self):
        Comment.add(blog_ident='abcdefg')

class TestTestingHelpers(object):

    def test_query_to_str_with_query(self):
        q = db.sess.query(Blog).filter(Blog.title == u'foo').limit(10).offset(5)
        query_str = query_to_str(q)
        assert 'SELECT' in query_str
        assert 'FROM blogs' in query_str
        assert 'WHERE blogs.title = \'foo\''
        assert 'LIMIT 10' in query_str, query_str
        assert 'OFFSET 5' in query_str

    def test_query_to_str_with_stmt(self):
        stmt = Blog.__table__.select().where(Blog.title == u'foo').limit(10).offset(5)
        stmt_str = query_to_str(stmt, db.engine)
        assert 'SELECT' in stmt_str
        assert 'FROM blogs' in stmt_str
        assert 'WHERE blogs.title = \'foo\''
        assert 'LIMIT 10' in stmt_str, stmt_str
        assert 'OFFSET 5' in stmt_str

    @raises('bind param (engine or connection object) required when using with an unbound statement')
    def test_query_to_str_without_bind(self):
        stmt = Blog.__table__.select()
        stmt_str = query_to_str(stmt)
