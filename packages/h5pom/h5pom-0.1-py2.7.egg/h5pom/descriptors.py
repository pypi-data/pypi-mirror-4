import string

class InstrumentedAttribute(object):
    pass


class H5pomInstrumentation(type):
    def __new__(cls, name, bases, attrs):
        cls.init_hdf5_attrs(name, bases, attrs)
        return super(H5pomInstrumentation, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def init_hdf5_attrs(cls, name, bases, attrs):
        # inject the attribute name from the class declaration into the decorator object
        for k, v in attrs.iteritems():
            if isinstance(v, InstrumentedAttribute):
                v.attrname = k
        if 'hdf5_loader_key' not in attrs:
            attrs['hdf5_loader_key'] = name


class Scalar(InstrumentedAttribute):
    """
    A Scalar is a member of a :class:`core.Object` which persists a python
    constant or simple type (e.g. int, str, bool, datetime, date, etc) to an
    attribute in the HDF5 group.  One should assume that items assigned to this
    class are an immutable type.  The details of which types are permissible
    depend on the implementation of :method:`core.Object._hdf5_scalar_load` and
    :method:`core.Object._hdf5_scalar_save` as well as h5py.
    """
    # NOTE:  Observe and maintain the slavish duplication of logic in Array,
    # Scalar, and SubObject.

    def persist(self, instance):
        a = self.attrname
        if instance.__dict__.has_key(a):
            instance._hdf5_scalar_save(a, instance.__dict__[a])

    def __get__(self, instance, owner):
        a = self.attrname
        if a not in instance.__dict__ and hasattr(instance, "_hdf5_group"):
            try:
                instance.__dict__[a] = instance._hdf5_scalar_load(a)
            except KeyError:
                pass
        if a not in instance.__dict__:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(instance.__class__.__name__, a))
        return instance.__dict__[a]

    def __set__(self, instance, value):
        a = self.attrname
        if hasattr(instance, "_hdf5_group"):
            instance._hdf5_scalar_save(a, value)
        instance.__dict__[a] = value


class Array(InstrumentedAttribute):
    """
    An Array is a member of a :class:`core.Object` which persists a numpy array
    to a dataset in the HDF5 group.

    Note the two major differences between this and a :class:`ScalarList`:
    - An Array expects a numpy array and so the storage in HDF5 is space and
      time efficient
    - A ScalarList returns an InstrumentedList which persists all modifications
      to the list.  An Array does not instrument the passed numpy array and so
      changes to this array must be explicitly propogated to storage (TODO:
      document the blessed way to do this!).
    """
    # NOTE:  Observe and maintain the slavish duplication of logic in Array,
    # Scalar, and SubObject.

    def persist(self, instance):
        a = self.attrname
        if instance.__dict__.has_key(a):
            instance._hdf5_array_save(a, instance.__dict__[a])
            instance.__dict__[a] = instance._hdf5_array_load(a) # regrab to get the

    def __get__(self, instance, owner):
        a = self.attrname
        if a not in instance.__dict__ and hasattr(instance, "_hdf5_group"):
            try:
                instance.__dict__[a] = instance._hdf5_array_load(a)
            except KeyError:
                pass
        if a not in instance.__dict__:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(instance.__class__.__name__, a))
        return instance.__dict__[a]

    def __set__(self, instance, value):
        a = self.attrname
        if hasattr(instance, "_hdf5_group"):
            instance._hdf5_array_delete(a)
            if value is not None:
                instance._hdf5_array_save(a, value)
                value = instance._hdf5_array_load(a) # regrab to get the
                                                     # instrumented array which
                                                     # h5py has for us
        instance.__dict__[a] = value


class SubObject(InstrumentedAttribute):
    """
    An SubObject is a member of a :class:`core.Object` which persists a python
    object reference and lazy loads it when the file is reopened.
    """
    # NOTE:  Observe and maintain the slavish duplication of logic in Array,
    # Scalar, and SubObject.

    def persist(self, instance):
        a = self.attrname
        if instance.__dict__.has_key(a):
            instance._hdf5_object_save(a, instance.__dict__[a])

    def __get__(self, instance, owner):
        a = self.attrname
        if a not in instance.__dict__ and hasattr(instance, "_hdf5_group"):
            try:
                instance.__dict__[a] = instance._hdf5_object_load(a)
            except KeyError:
                pass
        if a not in instance.__dict__:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(instance.__class__.__name__, a))
        return instance.__dict__[a]

    def __set__(self, instance, value):
        a = self.attrname
        if hasattr(instance, "_hdf5_group"):
            instance._hdf5_object_delete(a)
            if value is not None:
                instance._hdf5_object_save(a, value)
        instance.__dict__[a] = value


class MockListContainer:
    """
    Testing mock container for the use by the :class:`InstrumentedList`.  In
    addition to be a mock, this serves as documentation of methods of
    :class:`hdf5alchemy.Object` which are relevant to saving and restoring
    scalar lists.
    """
    def _hdf5_list_insert(self, a, l, begin, end):
        pass
    def _hdf5_list_delete(self, a, l, begin, end):
        pass
    def _hdf5_list_assign(self, a, l, index):
        pass


class InstrumentedList(object):
    """
    This is a list-like object which implements each method to notify the
    containing :class:`hdf5alchemy.Object` of the changes in the list so that
    it is persisted correctly to the storage.  The implementation semantics
    match the standard python list class although it may not be a complete
    implementation.  We'll implement until we cover 'enough' of the list
    implementation to quell complaints.

    >>> l = InstrumentedList(MockListContainer(), None)
    >>> l.append(1)
    >>> l.append(2)
    >>> len(l)
    2
    >>> len([x for x in l if x == 2])
    1
    >>> l[0]
    1
    >>> l[0:1]
    [1]
    >>> l.insert(1, 3)
    >>> l[1] = 15
    >>> (len(l), l[2])
    (3, 2)
    >>> del l[0]
    >>> l
    [15, 2]
    """
    def __init__(self, container, container_attr):
        self._container = container
        self._container_attr = container_attr
        self._value = []

    def __repr__(self):
        return repr(self._value)

    def append(self, x):
        self._value.append(x)
        self._container._hdf5_list_insert(self._container_attr, self._value, len(self._value)-1, len(self._value))

    def extend(self, L):
        prior = len(self._value)
        self._value.extend(L)
        self._container._hdf5_list_insert(self._container_attr, self._value, prior, len(self._value))

    def insert(self, i, x):
        self._value.insert(i, x)
        self._container._hdf5_list_insert(self._container_attr, self._value, i, i+1)

    def __delitem__(self, i):
        i = int(i) # only handle item assigns
        del self._value[i]
        self._container._hdf5_list_delete(self._container_attr, self._value, i, i+1)

    def __getitem__(self, i):
        return self._value[i]

    def __setitem__(self, i, v):
        i = int(i) # only handle item assigns
        self._value[i] = v
        self._container._hdf5_list_assign(self._container_attr, self._value, i)

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        for i in self._value:
            yield i


class ScalarList(InstrumentedAttribute):
    """
    A ScalarList is a member of a :class:`core.Object` which persists a python
    list of items to a prefixed array of attributes in the HDF5 group.
    """
    def persist(self, instance):
        a = self.attrname
        if instance.__dict__.has_key(a):
            instance._hdf5_list_save(a, instance.__dict__[a])

    def __get__(self, instance, owner):
        a = self.attrname
        if not instance.__dict__.has_key(a):
            instance.__dict__[a] = instance._hdf5_list_load(a)
        return instance.__dict__[a]

    def __set__(self, instance, value):
        a = self.attrname
        if hasattr(instance, "_hdf5_group"):
            instance._hdf5_list_purge(a)
        l = InstrumentedList(instance, a)
        l.extend(value)
        instance.__dict__[a] = l


class SubObjectList(ScalarList):
    """
    An SubObjectList is a member of a :class:`core.Object` which persists a
    python list of python object reference and lazy loads it when the file is
    reopened.
    """
    pass


class MockDictContainer:
    """
    Testing mock container for the use by the :class:`InstrumentedDict`.  In
    addition to be a mock, this serves as documentation of methods of
    :class:`hdf5alchemy.Object` which are relevant to saving and restoring
    scalar lists.
    """
    def _hdf5_dict_delete(self, a, d, key):
        pass
    def _hdf5_dict_assign(self, a, d, key):
        pass


class InstrumentedDict(object):
    """
    This is a dict-like object which implements each method to notify the
    containing :class:`hdf5alchemy.Object` of the changes in the dict so that
    it is persisted correctly to the storage.  The implementation semantics
    match the standard python dict class although it may not be a complete
    implementation.  We'll implement until we cover 'enough' of the dict
    implementation to quell complaints.

    Note that where Python 2.x and Python 3.x differ in functionality with the
    iteration of keys and values, this implementation tends to behave like
    python 3.x as it it generally more simple and sensible.

    >>> # In this example we use only scalars, but object references are
    >>> # equally supported (presuming the object type is registered when the
    >>> # hdf5 is opened).
    >>> l = InstrumentedDict(MockDictContainer(), None)
    >>> l[1] = "one"
    Traceback (most recent call last):
    ...
    ValueError: ...
    >>> l['one'] = 1
    >>> l['two'] = 2
    >>> len(l)
    2
    >>> del l['two']
    >>> list(l.keys())
    ['one']
    >>> list(l)
    ['one']
    >>> list(l.values())
    [1]
    >>> 'three' in l
    False
    >>> l
    {'one': 1}
    >>> l.get('one'), l.get('four')
    (1, None)
    """
    def __init__(self, container, container_attr):
        self._container = container
        self._container_attr = container_attr
        self._value = {}

    def __repr__(self):
        return repr(self._value)

    def keys(self):
        return self._value.iterkeys()

    def values(self):
        return self._value.itervalues()

    def items(self):
        return self._value.iteritems()

    def update(self, other):
        for k, v in other.iteritems():
            self[k] = v

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def __delitem__(self, key):
        del self._value[key]
        self._container._hdf5_dict_delete(self._container_attr, self._value, key)

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, v):
        if not isinstance(key, str) or not set(key).issubset(string.ascii_letters+string.digits+"_"):
            # The motivation for the following limitation is to ensure safe and
            # non-clashing names for groups and attributes in the HDF5 data
            # store.
            raise ValueError("Invalid key '{0}':  InstrumentedDict keys must be strings with characters only taken from alphanumeric and '_'.".format(key))
        self._value[key] = v
        self._container._hdf5_dict_assign(self._container_attr, self._value, key)

    def __len__(self):
        return len(self._value)

    def __contains__(self, key):
        return key in self._value

    def __iter__(self):
        for i in self._value:
            yield i


class SubObjectDict(InstrumentedAttribute):
    """
    An SubObjectDict is a member of a :class:`core.Object` which persists a
    python dict of python object reference and lazy loads it when the file is
    reopened.
    """
    def persist(self, instance):
        a = self.attrname
        if instance.__dict__.has_key(a):
            instance._hdf5_dict_save(a, instance.__dict__[a])

    def __get__(self, instance, owner):
        a = self.attrname
        if not instance.__dict__.has_key(a):
            instance.__dict__[a] = instance._hdf5_dict_load(a)
        return instance.__dict__[a]

    def __set__(self, instance, value):
        a = self.attrname
        if hasattr(instance, "_hdf5_group"):
            instance._hdf5_dict_purge(a)
        l = InstrumentedDict(instance, a)
        l.update(value)
        instance.__dict__[a] = l
