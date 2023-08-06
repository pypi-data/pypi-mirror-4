from sqlalchemy import types
from sqlalchemy.orm.properties import ColumnProperty


DEFAULT_EQUIVALENCE_OPTIONS = {
    'include_autoinc_primary_keys': False,
    'include_foreign_keys': False,
    'include': [],
    'exclude': [],
    'only': []
}


class NaturalEquivalence(object):
    @classmethod
    def _get_equivalence_option(cls, name):
        try:
            return cls.__equivalence_options__[name]
        except (AttributeError, KeyError):
            return DEFAULT_EQUIVALENCE_OPTIONS[name]

    def __eq__(self, other):
        """
        Defines natural equivalence between this object and other object.
        """
        fields = set(self._sa_class_manager.values())
        properties = map(lambda a: a.property, fields)
        filter_func = PropertyListFilter(self)
        properties = filter(filter_func, properties)

        if self.__class__ != other.__class__:
            return False

        for property_ in properties:
            if getattr(self, property_.key) != getattr(other, property_.key):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)


class PropertyListFilter(object):
    def __init__(self, obj):
        self.obj = obj

    def __call__(self, property_):
        if isinstance(property_, ColumnProperty):
            column = property_.columns[0]
            if (not self.obj._get_equivalence_option(
                    'include_autoinc_primary_keys') and
                    column.primary_key and
                    column.autoincrement and
                    is_integer_column(column)):
                return False

            if (not self.obj._get_equivalence_option('include_foreign_keys')
                    and column.foreign_keys):
                return False
        return True


def is_integer_column(column):
    return (
        isinstance(column.type, types.Integer) or
        isinstance(column.type, types.SmallInteger) or
        isinstance(column.type, types.BigInteger)
    )
