import sqlalchemy.types

class SmallIntBool(sqlalchemy.types.TypeDecorator):
    # A SmallInteger type that always saves as 0 or 1 on the DB side and has
    # a True/False value on the Python side

    impl = sqlalchemy.types.SmallInteger

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return int(bool(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return bool(value)
