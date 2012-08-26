import inspect

from flask.ext.admin.form import BaseForm


def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func
    return _inner


class InlineFormAdmin(object):
    def __init__(self, field, **kwargs):
        self.field = field

        defaults = dict(include=None,
                        exclude=None)
        defaults.update(kwargs)

        for k, v in defaults.iteritems():
            setattr(self, k, v)


class ModelConverterBase(object):
    def __init__(self, converters=None, use_mro=True):
        self.use_mro = use_mro

        if not converters:
            converters = {}

        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_converter_for'):
                for classname in obj._converter_for:
                    converters[classname] = obj

        self.converters = converters

    def get_converter(self, column):
        if self.use_mro:
            types = inspect.getmro(type(column.type))
        else:
            types = [type(column.type)]

        # Search by module + name
        for col_type in types:
            type_string = '%s.%s' % (col_type.__module__, col_type.__name__)

            if type_string in self.converters:
                return self.converters[type_string]

        # Search by name
        for col_type in types:
            if col_type.__name__ in self.converters:
                return self.converters[col_type.__name__]

        return None

    def get_form(self, model, base_class=BaseForm,
                only=None, exclude=None,
                field_args=None):
        raise NotImplemented()
