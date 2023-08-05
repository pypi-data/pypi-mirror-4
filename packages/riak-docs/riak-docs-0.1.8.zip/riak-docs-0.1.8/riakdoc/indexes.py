from time import time

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'
__all__ = ['BaseIndex', 'TimestampIndex', 'StrFieldsIndex']

class GetterShell(object):
    def __init__(self, index):
        self.index = index

    def __get__(self, instance, klass):
        """
        This getter could be changed to pass instance, but I like get_value() not having to check if the instance is None.
        """
        return self.index.get_value(instance.get_data() if instance else {}, instance.indexes or {})

class BaseIndex(object):
    def __init__(self, required=False, *args, **kwargs):
        """
        Create a named index on a document.
        """
        self.required = required
        self.name = None

    def set_name(self, name):
        self.name = name

    def update(self, data, indexes):
        """
        Called just before indexes are saved on a document.

        This method should just update indexes, nothing else.

        @param data: The data for the document.
        @type data: dict (or list)
        @param indexes: The indexes on the document as a dictionary.
        @type indexes: dict
        @rtype: None
        """
        value = self.get_value(data, indexes)
        if value is None:
            if self.required:
                raise ValueError('Index {0} is missing, cannot save.'.format(self.name))
            else:
                del indexes[self.name]
        else:
            indexes[self.name] = value

    def get_value(self, data, indexes):
        """
        Gets the value that will be set for this index based on the state of the data in the Riak document.

        @param data: Data in the Riak doc.
        @type data: dict
        """
        raise NotImplementedError()

class TimestampIndex(BaseIndex):
    """
    Update a timestamp index with every save or just initially. (See: on_every_save)
    """
    def __init__(self, required=False, on_every_save=False, *args, **kwargs):
        """
        @type name: str
        @type required: bool
        @param on_every_save: If true, update the timestamp every time the object is saved, otherwise just when
          initially saved.
        @type on_every_save: bool
        """
        self.on_every_save = on_every_save
        super(TimestampIndex, self).__init__(required=required, *args, **kwargs)

    def get_value(self, data, indexes):
        if self.on_every_save or not self.name in indexes:
            return int(time())
        else:
            return indexes[self.name]

class StrFieldsIndex(BaseIndex):
    def __init__(self, fields, required=False, separator='_', *args, **kwargs):
        """
        Use one (or more) fields as the value of an index.

        @type field: str
        @type required: bool
        @param separator: When joining multiple fields together, which string separator to use.
        @type separator: str
        @type name: str
        """
        if isinstance(fields, str):
            fields = [fields]
        self.fields = list(fields)
        self.required = required
        self.separator = separator
        super(StrFieldsIndex, self).__init__(*args, **kwargs)

    def get_value(self, data, indexes):
        values = []
        for field in self.fields:
            value = self.get_field_value(field, data)
            if not value:
                return None
            values.append(value)
        return self.separator.join(values)

    def get_field_value(self, field, data):
        bits = field.split('.')
        value = None
        d = data
        try:
            for bit in bits:
                d = d[bit]
            value = str(d)
        except (TypeError, KeyError, IndexError):
            pass

        return value