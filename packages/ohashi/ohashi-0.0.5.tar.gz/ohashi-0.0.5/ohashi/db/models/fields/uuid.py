import psycopg2.extras
import uuid

from ohashi.db.models.fields import CharField
from south.modelsinspector import add_introspection_rules


# Register this adapter so we can use UUID objects.
psycopg2.extras.register_uuid()


class UUIDField(CharField):
    """
    A field which stores a UUID value in hex format. This may also have the
    Boolean attribute 'auto' which will set the value on initial save to a new
    UUID value (calculated using the UUID4 method).

    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('editable', not kwargs.get('primary_key', False))
        super(UUIDField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'uuid'

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return None
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


# South custom field introspection rules.
add_introspection_rules([([UUIDField], [], {'auto': ['auto', {'default': 'False'}]},)], [r'^ohashi\.db\.fields\.UUIDField'])
