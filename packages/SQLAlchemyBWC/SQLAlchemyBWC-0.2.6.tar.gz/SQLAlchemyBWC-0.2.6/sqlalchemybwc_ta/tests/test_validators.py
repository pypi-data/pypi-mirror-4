from nose.tools import eq_
from savalidation import ValidationError
from sqlalchemybwc import db

from sqlalchemybwc_ta.model.orm import HasUniqueValidation

class TestUniqueValidation(object):

    def tearDown(cls):
        db.sess.remove()
        HasUniqueValidation.delete_all()

    def test_name_dup(self):
        HasUniqueValidation.add(name='a', email='b')
        try:
            HasUniqueValidation.add(name='a', email='c')
            assert False
        except ValidationError, e:
            expect = {'name': [u'the value for this field is not unique']}
            eq_(e.invalid_instances[0].validation_errors, expect)
        HasUniqueValidation.add(name='b', email='c')

    def test_email_dup(self):
        HasUniqueValidation.add(name='a', email='b')
        try:
            HasUniqueValidation.add(name='b', email='b')
            assert False
        except ValidationError, e:
            expect = {'email': [u'the value for this field is not unique']}
            eq_(e.invalid_instances[0].validation_errors, expect)
        HasUniqueValidation.add(name='b', email='c')

    def test_two_dups(self):
        HasUniqueValidation.add(name='a', email='b')
        try:
            HasUniqueValidation.add(name='a', email='b')
            assert False
        except ValidationError, e:
            expect = {'name': [u'the value for this field is not unique'],
                'email': [u'the value for this field is not unique']}
            eq_(e.invalid_instances[0].validation_errors, expect)
        HasUniqueValidation.add(name='b', email='c')

    def test_ok_edit(self):
        inst = HasUniqueValidation.add(name='a', email='b')
        inst.email = 'c'
        db.sess.commit()
        db.sess.remove()
        inst = HasUniqueValidation.get_by(name='a')
        assert inst.email == 'c'

    def test_validate_unique_edit(self):
        inst1 = HasUniqueValidation.add(name='a', email='b')
        inst2 = HasUniqueValidation.add(name='c', email='d')
        inst2.email = 'b'
        try:
            db.sess.commit()
            assert False
        except ValidationError, e:
            db.sess.rollback()
            expect = {'email': [u'the value for this field is not unique']}
            eq_(e.invalid_instances[0].validation_errors, expect)
        # setting it back should work
        inst2.email = 'd'
        db.sess.commit()
        db.sess.remove()
        inst = HasUniqueValidation.get_by(name='c')
        assert inst.email == 'd'
        # setting it to something else should also work
        inst.email = 'e'
        db.sess.commit()
        db.sess.remove()
        inst = HasUniqueValidation.get_by(name='c')
        assert inst.email == 'e'
