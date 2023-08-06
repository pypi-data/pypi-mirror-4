
import h5py
import datetime
import numpy
import h5pom.descriptors as descriptors

IN_MEMORY = "."
loader_key = 'loader-key'
folder_key = 'Folder'

class FileInstance(object):
    def __init__(self, mappers):
        self._root = None
        self.mapdict = {}
        for m in mappers:
            k = m.hdf5_loader_key
            self.mapdict[k] = m

        if folder_key not in self.mapdict:
            self.mapdict[folder_key] = Folder

        # We ensure Fowler's identity pattern by the group id.  Note that the
        # name is not a sufficiently unique key being ambiguous when a group is
        # linked to multiple parent groups with HDF5 links.
        self.identity_map = {}

    def openFile(self, fname):
        if fname is IN_MEMORY:
            self.hdf5file = h5py.File(fname, driver='core', backing_store=False)
        else:
            self.hdf5file = h5py.File(fname, 'a')

    def close(self):
        self.identity_map = {}
        self.hdf5file.close()

    def register(self, grp, obj):
        self.identity_map[grp.id] = obj

    def unregister(self, grp):
        del self.identity_map[grp.id]

    def group_object_load(self, grp):
        if self.identity_map.has_key(grp.id):
            return self.identity_map[grp.id]
        else:
            key = grp.attrs.get(loader_key)
            obj = self.mapdict.get(key)
            if obj is None:
                obj = self.mapdict.get(folder_key)
            if obj is None:
                obj = Folder # this is a default, but is that what we want?
            # I think this should not call __init__ -- similar to how
            # SQLAlchemy and pickles reconstruct an object through the back
            # door.  The supporting logic is that __init__ should be for class
            # initialization, but reloading is reloading which is distinct from
            # the original initialization.  Here are some pros and cons.
            # * Reasons to call __init__:
            #   - non-persisted member initialization is natural in __init__
            # * Reasons to not call __init__:
            #   - lots of __init__ code is superflous for deserialization
            #   - automated duplication (e.g. generic export routine) of
            #     objects needs to be aware of the ramification of load/reload
            #     and save in new enviroment anyhow - skipping __init__ forces 
            #     the reloading workflow to be explicit
            #   - parameters to __init__ may be for the joy of the app
            #     programmer and are not known here
            r = obj.__new__(obj)
            # NOTE:  all h5pom attributes are lazy loaded.
            r._hdf5_instance = self
            r._hdf5_group = grp
            r._hdf5_init_()
            r._hdf5_reload_()
            self.register(grp, r)
            return r

    @property
    def root(self):
        if self._root is None:
            self._root = self.group_object_load(self.hdf5file)
        return self._root

class Duplicator(FileInstance):
    """
    Associates a duplicate FileInstance with a single HDF5 file handle.  This
    duplicate can be used to load a second copy of objects.  These objects can
    then be saved to other HDF5 instances through the usual means.  The
    duplicated objects are initialized in the usual way, but they are
    associated with this derivative of :class:`FileInstance` and so the
    identity map allows the objects to have two instances in memory.

    This class is designed to be used as a context manager.  This is
    recommended and enforces the eager loading mechanism and disconnects the
    objects from this Duplicator so that they can be saved in a new HDF5 file.

    >>> f=open(IN_MEMORY, [])
    >>> with Duplicator(f) as d:
    ...     f2 = d.duplicate(f)
    """
    def __init__(self, obj):
        self._root = None
        self.mapdict = obj._hdf5_instance.mapdict
        self.identity_map = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k, v in self.identity_map.iteritems():
            if not isinstance(v, Object):
                # exclude datasets
                continue
            del v._hdf5_instance
            del v._hdf5_group

    def duplicate(self, obj):
        v = self.group_object_load(obj._hdf5_group)
        v._hdf5_eager_load()
        return v


def open(fname, mapped_classes):
    f = FileInstance(mappers=mapped_classes)
    f.openFile(fname)
    return f.root


class Object(object):
    """
    This the base class for h5pom mapped objects.  Objects are distinct from
    scalars which are always leaf nodes on the object tree.  This Object class
    is not instantiated for scalars.
    """
    __metaclass__ = descriptors.H5pomInstrumentation

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self._hdf5_init_()

    def _hdf5_init_(self):
        pass

    def _hdf5_reload_(self):
        pass

    def _hdf5_scalar_save(self, a, v):
        grp = self._hdf5_group
        typestr = None
        if v is None:
            typestr = 'None'
            v = 0
        elif isinstance(v, datetime.datetime):
            typestr = 'datetime'
            # to save as tuple is an idea from Larry -- http://pypi.python.org/pypi/la
            v = numpy.array((v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond))
        elif isinstance(v, datetime.date):
            typestr = 'date'
            # to save as tuple is an idea from Larry -- http://pypi.python.org/pypi/la
            v = numpy.array((v.year, v.month, v.day))
        elif isinstance(v, unicode):
            v = str(v)
        typelabel = '{0}-type'.format(a)
        try:
            if typestr is None:
                if typelabel in grp.attrs:
                    del grp.attrs[typelabel]
            else:
                grp.attrs[typelabel] = typestr
        except Exception as e:
            raise RuntimeError("error adding attribute '{0}' (value {3}) under group '{1}' ({2})".format(typelabel, grp.name, str(e), str(typestr)))
        try:
            grp.attrs[a] = v
        except Exception as e:
            raise RuntimeError("error adding attribute '{0}' (value {3}) under group '{1}' ({2})".format(a, grp.name, str(e), str(v)))

    def _hdf5_scalar_load(self, a):
        grp = self._hdf5_group
        v = grp.attrs[a]
        typelabel = '{0}-type'.format(a)
        typestr = grp.attrs.get(typelabel, None)
        if typestr == 'None':
            v = None
        elif typestr == 'date':
            v = datetime.date(*tuple(v))
        elif typestr == 'datetime':
            v = datetime.datetime(*tuple(v))
        return v

    def _hdf5_scalar_move(self, olda, newa):
        self._hdf5_scalar_save(newa, self._hdf5_scalar_load(olda))

    def _hdf5_extscalar_save(self, a, v):
        if isinstance(v, Object):
            self._hdf5_object_save(a, v)
        else:
            self._hdf5_scalar_save(a, v)

    def _hdf5_extscalar_load(self, a):
        if a in self._hdf5_group:
            return self._hdf5_object_load(a)
        else:
            return self._hdf5_scalar_load(a)

    def _hdf5_extscalar_move(self, olda, newa):
        if olda in self._hdf5_group:
            self._hdf5_object_move(olda, newa)
        else:
            self._hdf5_scalar_move(olda, newa)

    def _hdf5_extscalar_delete(self, a):
        if a in self._hdf5_group:
            del self._hdf5_group[a]
        if a in self._hdf5_group.attrs:
            del self._hdf5_group.attrs[a]
        at = "{0}-type".format(a)
        if at in self._hdf5_group.attrs:
            del self._hdf5_group.attrs[at]

    def _hdf5_list_load(self, a):
        v = descriptors.InstrumentedList(self, a)
        if hasattr(self, "_hdf5_group"):
            grp = self._hdf5_group
            count = grp.attrs.get("{0}-count".format(a), 0)
            v._value = [self._hdf5_extscalar_load('{0}-{1}'.format(a, i)) for i in range(count)]
        return v

    def _hdf5_list_purge(self, a):
        grp = self._hdf5_group
        grp.attrs["{0}-count".format(a)] = 0
        prefix = "{0}-".format(a)
        for k in grp.attrs.keys():
            if k.startswith(prefix) and not k.endswith("count"):
                del grp.attrs[k]

    def _hdf5_list_save(self, a, l):
        grp = self._hdf5_group
        count = len(l)
        grp.attrs["{0}-count".format(a)] = count
        for index in range(count):
            self._hdf5_extscalar_save('{0}-{1}'.format(a, index), l[index])

    def _hdf5_list_insert(self, a, l, begin, end):
        if not hasattr(self, "_hdf5_group"):
            return
        grp = self._hdf5_group
        count = len(l)
        grp.attrs["{0}-count".format(a)] = count
        for index in range(count-1, end-1, -1):
            old_index = index - (end-begin)
            self._hdf5_extscalar_move('{0}-{1}'.format(a, old_index), '{0}-{1}'.format(a, index))
        for index in range(begin, end):
            self._hdf5_extscalar_save('{0}-{1}'.format(a, index), l[index])

    def _hdf5_list_delete(self, a, l, begin, end):
        if not hasattr(self, "_hdf5_group"):
            return
        grp = self._hdf5_group
        count = len(l)
        grp.attrs["{0}-count".format(a)] = count
        old_count = count + (end-begin)
        for index in range(end, old_count):
            new_index = index - (end-begin)
            self._hdf5_extscalar_move('{0}-{1}'.format(a, index), '{0}-{1}'.format(a, new_index))
        for index in range(end-begin):
            del_index = count-index
            self._hdf5_extscalar_delete('{0}-{1}'.format(a, del_index))

    def _hdf5_list_assign(self, a, l, index):
        if not hasattr(self, "_hdf5_group"):
            return
        self._hdf5_extscalar_save('{0}-{1}'.format(a, index), l[index])

    def _hdf5_dict_save(self, a, d):
        for k, v in d.items():
            self._hdf5_extscalar_save('{0}-{1}'.format(a, k), v)

    def _hdf5_dict_load(self, a):
        v = descriptors.InstrumentedDict(self, a)
        if hasattr(self, "_hdf5_group"):
            prefix = "{0}-".format(a)
            grp = self._hdf5_group
            v._value = {key[len(prefix):]: self._hdf5_extscalar_load(key) for key in list(grp.attrs.keys()) + list(grp) if key.startswith(prefix)}
        return v

    def _hdf5_dict_purge(self, a):
        prefix = "{0}-".format(a)
        grp = self._hdf5_group
        for key in list(grp):
            if key.startswith(prefix):
                del grp[key]

    def _hdf5_dict_delete(self, a, d, key):
        if not hasattr(self, "_hdf5_group"):
            return
        self._hdf5_extscalar_delete('{0}-{1}'.format(a, key))

    def _hdf5_dict_assign(self, a, d, key):
        if not hasattr(self, "_hdf5_group"):
            return
        # TODO (maybe):  Support scalar valued dictionaries.
        assert isinstance(d[key], Object)
        self._hdf5_extscalar_delete('{0}-{1}'.format(a, key))
        self._hdf5_extscalar_save('{0}-{1}'.format(a, key), d[key])

    def _hdf5_generic_delete(self, a):
        if a in self._hdf5_group:
            self._hdf5_instance.unregister(self._hdf5_group[a])
            del self._hdf5_group[a]

    def _hdf5_array_save(self, a, v):
        grp = self._hdf5_group
        sds = grp.create_dataset(a, data=v, chunks=True, maxshape=tuple(None for i in v.shape))
        self._hdf5_instance.register(sds, v)

    def _hdf5_array_load(self, a):
        sds = self._hdf5_group[a]
        self._hdf5_instance.register(sds, sds)
        return sds

    _hdf5_array_delete = _hdf5_generic_delete

    @staticmethod
    def _hdf5_class_attrs(cls):
        fulldict = {}
        for class_ in reversed(cls.mro()):
            for k, instattr in class_.__dict__.iteritems():
                if isinstance(instattr, descriptors.InstrumentedAttribute):
                    fulldict[k] = instattr
        return fulldict

    def _hdf5_object_save(self, a, v):
        grp = self._hdf5_group

        if hasattr(v, "_hdf5_group"):
            # make a hard-link and quit!
            grp[a] = v._hdf5_group
            return

        sgrp = grp.create_group(a)
        sgrp.attrs[loader_key] = v.hdf5_loader_key
        v._hdf5_instance = self._hdf5_instance
        v._hdf5_group = sgrp
        self._hdf5_instance.register(sgrp, v)

        for k, instattr in Object._hdf5_class_attrs(v.__class__).iteritems():
            instattr.persist(v)

    def _hdf5_object_load(self, a):
        return self._hdf5_instance.group_object_load(self._hdf5_group[a])

    def _hdf5_object_move(self, olda, newa):
        # the semantics of _hdf5_scalar_move is to overwrite, we duplicate
        # those semantics here!
        if newa in self._hdf5_group:
            del self._hdf5_group[newa]
        # move the group using the low-level HDF5 routine
        self._hdf5_group.id.move(olda, newa)

    _hdf5_object_delete = _hdf5_generic_delete

    def _hdf5_eager_load(self):
        for k, instattr in Object._hdf5_class_attrs(self.__class__).iteritems():
            v = None
            try:
                v = getattr(self, instattr.attrname)
            except AttributeError:
                pass
            if v is not None:
                if isinstance(v, Object):
                    v._hdf5_eager_load()
                elif isinstance(v, descriptors.InstrumentedList):
                    for item in v:
                        item._hdf5_eager_load()
                elif isinstance(v, descriptors.InstrumentedDict):
                    for key, item in v.items():
                        item._hdf5_eager_load()

    @property
    def _hdf5_parent(self):
        return self._hdf5_instance.group_object_load(self._hdf5_group.parent)


class Folder(Object):
    def _hdf5_init_(self):
        self._hdf5_subs = {}

    def __getitem__(self, key):
        if not self._hdf5_subs.has_key(key):
            self._hdf5_subs[key] = self._hdf5_object_load(key)
        return self._hdf5_subs[key]

    def __setitem__(self, key, v):
        self._hdf5_object_save(key, v)
        self._hdf5_subs[key] = v

    def __delitem__(self, key):
        self._hdf5_object_delete(key)

    def __contains__(self, key):
        return key in self._hdf5_group

    @property
    def attrs(self):
        class AttrDict(object):
            def __init__(self, my_folder):
                self.folder = my_folder

            def __getitem__(self, key):
                return self.folder._hdf5_scalar_load(key)

            def __setitem__(self, key, v):
                self.folder._hdf5_scalar_save(key, v)

        return AttrDict(self)

    @property
    def parent(self):
        return self._hdf5_parent

    def close(self):
        if self._hdf5_group.name != '/':
            raise RuntimeError("The file close is only allowed for the root folder.")
        self._hdf5_instance.close()
