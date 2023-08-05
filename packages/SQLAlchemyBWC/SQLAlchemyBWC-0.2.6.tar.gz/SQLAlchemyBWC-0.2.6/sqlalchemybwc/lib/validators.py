from blazeutils.datastructures import BlankObject
import formencode
from savalidation.validators import EntityLinker, ValidatorBase
from sqlalchemy import sql as sasql

from compstack.sqlalchemy import db

class _UniqueValidator(formencode.validators.FancyValidator):
    """
    Calls the given callable with the value of the field.  If the return value
    does not evaluate to false, Invalid is raised
    """

    __unpackargs__ = ('fieldname', 'cls', 'instance')
    messages = {
        'notunique': u'the value for this field is not unique',
        }

    def validate_python(self, value, state):
        existing_record = self.cls.get_by(**{self.fieldname:value})
        if existing_record and existing_record is not state.entity:
            raise formencode.Invalid(self.message('notunique', state), value, state)

class _UniqueValidationHandler(ValidatorBase):
    type = 'field'
    def create_fe_validators(self):
        if not self.field_names:
            raise ValueError('validates_unique() must be passed at least one field name')
        for field_to_validate in self.field_names:
            valinst = _UniqueValidator(
                cls = self.entitycls,
                fieldname = field_to_validate
            )
            self.create_fev_meta(valinst, field_to_validate)

validates_unique = EntityLinker(_UniqueValidationHandler)
