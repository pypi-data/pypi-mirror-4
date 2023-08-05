from blinker import signal
import copy
from riak import RiakHttpTransport, RiakClient
from riakdoc.keygen import simple_hex_key
from riakdoc.indexes import BaseIndex, GetterShell

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'
__all__ = ['BaseRiakDocument']


class BaseDocumentMeta(type):
    def __new__(mcs, name, bases, d):
        """
        Sets up a document class.

        2i Indexes:
            This metaclass takes `riakdoc.indexes.BaseIndex` subclasses and puts a getter around them so that they
            can provide the actual value of the index, were it to be saved, as well as saving the index object in `_indexes`
            Example: if you have my_index = TimestampIndex(), then the new object will have:
                new_object.my_index # will be an int
                new_object._indexes['my_index'] # which will contain the actual BaseIndex subclass.
        """
        d['_indexes'] = {}
        for k in d:
            if isinstance(d[k], BaseIndex):
                d[k].set_name(k)
                d['_indexes'][k] = d[k]
                d[k] = GetterShell(d[k])
        return super(BaseDocumentMeta, mcs).__new__(mcs, name, bases, d)

class BaseDocument(object):
    """
    Subclass-able Riak Document class.

    Default Signals:
        pre-document save   - Called right before document storage in Riak, sender is class, document kwarg is instance.
        post-document save  - Called right after document save in Riak, sender is class, document kwarg is instance.
        data initialized    - Called right after initialize_data, sender is class, document kwarg is instance.
    """
    clients = {}
    using = None
    bucket_name = None
    enable_2i = None
    keygen_func = simple_hex_key

    __metaclass__ = BaseDocumentMeta

    def __init__(self, key, obj=None, d=None, using=None, noclobber=True, indexes=None, *args, **kwargs):
        """
        Create a basic Riak model.

        @param key: The key to store/retrieve from Riak.
        @type key: str
        @param obj: A seed object to use for this model.
        @type obj: riak.riak_object.RiakObject
        @param d: A seed dictionary to use.
        @type d: dict
        @param using: Name of the Riak connection to use.
        @type using: str
        @param noclobber: Whether or not to accept both a `d` and a `obj` with data.
        @type noclobber: bool
        """
        self.key = str(key)
        if not obj:
            obj = self.get_bucket(using=using).get(self.key)
            obj.set_content_type('application/json')
        self._obj = obj

        self.indexes = {}
        if self.using_2i(using=using):
            for ri in self._obj.get_indexes():
                self.indexes[ri.get_field()] = ri.get_value()
            if indexes:
                self.indexes.update(indexes)

        if d:
            if self._obj.exists() and self._obj.get_data() and noclobber:
                raise Exception('No clobber set but data and Riak object passed.')
            self.data = d
            self._obj.set_data(d)
        else:
            if self._obj.exists():
                self.data = obj.get_data()
            else:
                self.data = self.initialize_data(*args, **kwargs)
                signal('data initialized').send(self.__class__, document=self)

    def __unicode__(self):
        return u'{0} document "{1}": {2}'.format(self.__class__.__name__, self.key, str(self.data)[:100])

    def __repr__(self):
        return "{klass}('{key}', d={data})".format(klass=self.__class__.__name__, key=self.key, data=repr(self.data))

    def __str__(self):
        return str(self.__unicode__())

    def using_2i(self, using=None):
        """
        Figure out if this object is supposed to use 2i or not. (2i is enabled as a backend option.)

        @param using: The name of the connection to use.
        @type using: str
        @rtype: bool
        """
        if self.enable_2i is not None:
            return self.enable_2i
        return self.get_config_for(using=using).get('ENABLE_2I', False)

    @classmethod
    def create(cls, keygen_func=None, *args, **kwargs):
        """
        Shortcut for creating an object without providing a key.

        Uses a keygen func to generate it, which can be specified per class or passed in.
        """
        key = keygen_func(cls, *args, **kwargs) if keygen_func else cls.keygen_func(*args, **kwargs)
        return cls(key, *args, **kwargs)

    @classmethod
    def get_config(cls):
        """
        Return the config dict.
        @rtype: dict
        """
        from riakdoc.settings import config
        return config.get()

    @classmethod
    def get_config_for(cls, using=None):
        """
        Get the configuration for a given connection name.

        @param using: The name of the client to use.
        @type using: str
        @rtype: dict
        """
        using = using or cls.using or 'DEFAULT'
        try:
            return cls.get_config()['DATABASES'][using]
        except KeyError:
            raise Exception('Improperly configured riakdoc database configuration for {0}'.format(using))

    @classmethod
    def get_or_create_client(cls, using=None):
        """
        Returns a new instance of a riak.RiakClient based on the name and the project settings.
        """
        using = using or cls.using or 'DEFAULT'

        if not using in cls.clients:
            settings = cls.get_config_for(using=using)
            cls.clients[using] = RiakClient(
                host=settings.get('HOST', 'localhost'),
                port=settings.get('PORT', 8098),
                prefix=settings.get('PREFIX', 'riak'),
                mapred_prefix=settings.get('MAPRED_PREFIX', 'mapred'),
                transport_class=settings.get('TRANSPORT', RiakHttpTransport),
                solr_transport_class=settings.get('SOLR_TRANSPORT', None)
            )
        return cls.clients[using]

    @classmethod
    def get_if_exists(cls, key, using=None):
        """
        @todo: Should this be in a Manager style object?
        """
        riak_obj = cls.get_or_create_client(using=using).bucket(cls.get_bucket_name()).get(key)
        if riak_obj.exists():
            return cls(key, obj=riak_obj)
        else:
            return None

    @classmethod
    def get_bucket(cls, using=None):
        """
        Returns the Riak bucket to use.
        @param using: The name of the connection to use.
        @type using: str
        @rtype: riak.RiakBucket
        """
        try:
            return cls._bucket
        except AttributeError:
            cls._bucket = cls.get_or_create_client(using=using).bucket(cls.get_bucket_name())
            return cls._bucket

    @classmethod
    def get_bucket_name(cls):
        """
        Returns the bucket name for this document (cls.bucket_name or cls.__name__)

        TODO: Does this actually have to be a class method anymore? Probably not, since it's only used in __init__ of
        this class.

        You could override this if you wanted to do something fancy with get_bucket_name, but pretty much nothing of
        value is passed in due to this being a class method.

        @rtype: str
        """
        return cls.bucket_name or cls.__name__

    def initialize_data(self, *args, **kwargs):
        """
        Called when the object is created without existing in Riak, *must return the data this object should have.*

        @param args: Any extra arguments to the constructor end up here.
        @param kwargs: Any extra kwargs from the constructor end up here.
        """
        return {}

    def save(self, using=None, *args, **kwargs):
        """
        Save the object in Riak.
        """
        self._obj.set_data(self.data)

        if self.using_2i(using=using):
            indexes = copy.deepcopy(self.indexes)
            for i in self._indexes.itervalues():
                i.update(self.data, indexes)
            indexes = self.update_indexes(indexes)
            self._obj.set_indexes([(k, indexes[k]) for k in indexes])
            self.indexes = indexes

        signal('pre-document save').send(self.__class__, document=self)
        self._obj.store()
        signal('post-document save').send(self.__class__, document=self)

    def update_indexes(self, indexes):
        """
        Override this to add custom indexery to this a document class.

        You must RETURN the updated indexes, simply updating index don't worky.

        @type indexes: dict
        @rtype: dict
        """
        return indexes

    def delete(self):
        """
        Delete this object's contents on the server.
        """
        self._obj.delete()

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    # I don't want to write out everything like .append() :)
    def __getattr__(self, item):
        return getattr(self.data, item)