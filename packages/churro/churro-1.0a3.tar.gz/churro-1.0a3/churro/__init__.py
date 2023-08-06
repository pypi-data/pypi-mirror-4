import acidfs
import datetime
import json
import sys
import transaction

from .collection_wrappers import DictWrapper
from .collection_wrappers import ListWrapper

CHURRO_EXT = '.churro'
CHURRO_FOLDER = '__folder__' + CHURRO_EXT

if sys.version_info[0] == 2: # pragma NO COVER
    DECODE_MODE = 'rb'
    ENCODE_MODE = 'wb'
else:  # pragma NO COVER
    DECODE_MODE = 'r'
    ENCODE_MODE = 'w'


class Churro(object):
    """
    **Constructor Arguments**

    ``repo``

       The path to the repository in the real, local filesystem.

    ``head``

       The name of a branch to use as the head for this transaction.  Changes
       made using this instance will be merged to the given head.  The default,
       if omitted, is to use the repository's current head.

    ``factory``

       A callable that returns the root database object to be stored as the
       root when creating a new database.  The default factory returns an
       instance of `churro.PersistentFolder`.  This has no effect if the
       repository has already been created.

    ``create``

       If there is not a Git repository in the indicated directory, should one
       be created?  The default is `True`.

    ``bare``

       If the Git repository is to be created, create it as a bare repository.
       If the repository is already created or `create` is False, this argument
       has no effect.
    """
    session = None

    def __init__(self, repo, head='HEAD',
                 factory=None, create=True, bare=False):
        self.fs = acidfs.AcidFS(repo, head=head, create=create, bare=bare,
                                name='Churro.AcidFS')
        if factory is None:
            factory = PersistentFolder
        self.factory = factory

    def _session(self):
        """
        Make sure we're in a session.
        """
        if not self.session or self.session.closed:
            self.session = _Session(self.fs)
        return self.session

    def root(self):
        """
        Gets the root folder of the repository.  This is the starting point for
        traversing to other objects in the repository.
        """
        return self._session().get_root(self.factory)

    def flush(self):
        """
        Writes any unsaved data to the underlying `AcidFS` filesystem without
        committing the transaction.
        """
        self._session().flush()


_marker = object()
_removed = object()


class reify(object):
    # Stolen from Pyramid
    """ Put the result of a method which uses this (non-data)
    descriptor decorator in the instance dict after the first call,
    effectively replacing the decorator with an instance variable."""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class JsonCodec(object):
    """
    Encodes/decodes Python objects as JSON.
    """
    @staticmethod
    def encode_hook(obj):
        if not isinstance(obj, Persistent):
            return obj

        cls = type(obj)
        dotted_name = '%s.%s' % (cls.__module__, cls.__name__)
        data = {}
        for member in cls.mro():
            for name, prop in member.__dict__.items():
                if not isinstance(prop, PersistentProperty):
                    continue
                if name not in data:
                    data[name] = prop.to_json(prop.__get__(obj))
        return {
            '__churro_class__': dotted_name,
            '__churro_data__': data}

    def encode(self, obj, stream):
        json.dump(obj, stream, default=self.encode_hook, indent=4)

    @staticmethod
    def decode_hook(data):
        if '__churro_class__' not in data:
            return data

        cls = _resolve_dotted_name(data['__churro_class__'])
        obj = cls.__new__(cls)
        for name, value in data['__churro_data__'].items():
            prop = getattr(cls, name)
            prop.__set__(obj, prop.from_json(value), False)

        return obj

    def decode(self, stream):
        return json.load(stream, object_hook=self.decode_hook)


codec = JsonCodec()


class PersistentType(type):

    def __init__(cls, name, bases, members):
        type.__init__(cls, name, bases, members)
        for name, prop in members.items():
            if isinstance(prop, PersistentProperty):
                prop.set_name(name)


PersistentBase = PersistentType('PersistentBase', (object,), {})


class PersistentProperty(object):
    """
    The base type for all persistent properties.  This property type can handle
    any data type as a value that is serializable natively to JSON.  Other types
    are implemented by extending this class and overriding the `from_json`,
    `to_json`, and `validate` methods.
    """
    default = None

    def set_name(self, name):
        self.attr = '.' + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.attr, self.default)

    def __set__(self, obj, value, set_dirty=True):
        if set_dirty:
            obj.set_dirty()
        if isinstance(value, Persistent):
            value.__setinstance__(obj.__instance__)
        return setattr(obj, self.attr, self.validate(value))

    def from_json(self, value):
        """
        Converts a value from its JSON representation to a Python object.
        """
        return value

    def to_json(self, value):
        """
        Converts a value from a Python object to an object that can be
        serialized as JSON.
        """
        return value

    def validate(self, value):
        """
        Used at assignment time to validate a value.  If a value is not of the
        proper type and cannot be converted to the proper type, a `ValueError`
        is raised, otherwise the valua is returned, including any transformation
        or coercion that has been performed."""
        return value


class PersistentDate(PersistentProperty):
    """
    A persistent attribute type that can store instances of `datetime.date`.
    """

    def from_json(self, value):
        if value:
            return datetime.date(*map(int, value.split('-')))
        return value

    def to_json(self, value):
        if value:
            return '%s-%s-%s' % (value.year, value.month, value.day)
        return value

    def validate(self, value):
        if value is not None and not isinstance(value, datetime.date):
            raise ValueError("%s is not an instance of datetime.date")
        return value


class PersistentDatetime(PersistentProperty):
    """
    A persistent attribute type that can store instances of `datetime.datetime`.
    """

    def from_json(self, value):
        if value:
            d, t = value.split('T')
            year, month, day = map(int, d.split('-'))
            hour, minute, second = map(int, t.split(':'))
            return datetime.datetime(year, month, day, hour, minute, second)
        return value

    def to_json(self, value):
        if value:
            return '%04d-%02d-%02dT%02d:%02d:%02d' % (
                value.year, value.month, value.day, value.hour, value.minute,
                value.second)
        return value

    def validate(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise ValueError("%s is not an instance of datetime.datetime")
        return value


class Persistent(PersistentBase):
    """
    This is the base class from which all persistent classes for `Churro` must
    be derived.  Only objects which are instances of a class derived from
    `Persistent` may be stored in a `Churro` repository.
    """
    _dirty = True
    __name__ = None
    __parent__ = None
    _fs = None

    def __new__(cls, *args, **kw):
        obj = super(Persistent, cls).__new__(cls)
        obj.__instance__ = obj
        return obj

    def __setinstance__(self, instance):
        self.__instance__ = instance

    def set_dirty(self):
        """
        Calling this method alerts `Churro` that this object is `dirty` and
        should be persisted at commit time.  It is usually not necesary to call
        this method from application code, since `Churro` tries to detect
        object mutation whenever possible.  You may need to call this method
        from your application code, however, if you use mutable data structures
        that are not themselves `Persistent` as values of persistent properties,
        as `Churro` has no way of detecting mutations to those structures.
        """
        node = self.__instance__
        while node is not None:
            node._dirty = True
            node = getattr(node, '__parent__', None)

    def deactivate(self):
        """
        Calling this method on a persistent object detaches that object, and
        its children, from the in memory persistent object tree, potentially
        allowing it to be garbage collected if there are no other references to
        the object.
        """
        # If this method is called on a nested object, we can't really detach
        # the nested object by itself, but we can detach the top level instance.
        instance = self.__instance__

        # Only the root node will not have a parent folder.
        folder = instance.__parent__
        if folder is None:
            # Can't really deatch root, just silently ignore
            return

        type = 'folder' if isinstance(instance, PersistentFolder) else 'object'
        if instance._dirty:
            node = instance
            while node._fs is None:
                node = node.__parent__
            folder._save(node._fs)
        folder._contents[instance.__name__] = (type, None)


class PersistentFolder(Persistent):
    """
    Classes which derive from this class are not only persistent in `Churro` but
    have dict-like properties allowing them to contain children which are
    other persistent objects or folders.  Storing an instance of
    `PersistentFolder` in a `Churro` repository, creates a folder in the
    underlying filesystem, in which child objects are stored.  Instances of
    `PersistentFolder` are dict-like and are interacted with in the same way as
    standard Python dictionaries.
    """
    @reify
    def _contents(self):
        contents = {}
        fs = self._fs
        if fs is None:
            return contents
        path = resource_path(self)
        with fs.cd(path):
            for fname in fs.listdir():
                if fname == CHURRO_FOLDER:
                    continue
                if fs.isdir(fname):
                    folder_data = '%s/%s' % (fname, CHURRO_FOLDER)
                    if fs.exists(folder_data):
                        contents[fname] = ('folder', None)
                elif fname.endswith(CHURRO_EXT):
                    contents[fname[:-7]] = ('object', None)
        return contents

    @property
    def _filtered_contents(self):
        return dict([(name, (type, obj)) for name, (type, obj)
                in self._contents.items() if obj is not _removed])

    def keys(self):
        """
        Returns the names of child objects.
        """
        return self._filtered_contents.keys()

    def values(self):
        """
        Returns an iterator over child objects.
        """
        for name, value in self.items():
            yield value

    def __iter__(self):
        """
        Returns an iterator over child names.
        """
        return iter(self._filtered_contents.keys())

    def items(self):
        """
        Returns an iterator over (child object's name, child object) tuples.
        """
        contents = self._filtered_contents
        for name, (type, obj) in contents.items():
            if obj is None:
                obj = self._load(name, type)
            yield name, obj

    def __len__(self):
        """
        Returns the number of children.
        """
        return len(self._filtered_contents)

    def __nonzero__(self):
        """
        Returns boolean indicating whether folder has any children.
        """
        return bool(self._filtered_contents)

    def __getitem__(self, name):
        """
        Retreives the child object of the given name.  Raises `KeyError` if the
        child is not found.
        """
        obj = self.get(name, _marker)
        if obj is _marker:
            raise KeyError(name)
        return obj

    def get(self, name, default=None):
        """
        Returns the child object of the given name.  Returns `default` if the
        child is not found.
        """
        contents = self._filtered_contents
        objref = contents.get(name)
        if not objref:
            return default
        type, obj = objref
        if obj is None:
            obj = self._load(name, type)
        return obj

    def __contains__(self, name):
        """
        Returns boolean indicating whether a child with the given name exists
        in the folder.
        """
        return name in self.keys()

    def __setitem__(self, name, other):
        """
        Adds a child to the folder with the given name.  If there is already
        another child with the same name in the folder, that child is
        overwritten.
        """
        type = 'folder' if isinstance(other, PersistentFolder) else 'object'
        self._contents[name] = (type, other)
        other.__parent__ = self
        other.__name__ = name
        _set_dirty(other)

    def __delitem__(self, name):
        """
        Removes the child with the given name from  the folder.  Raises
        `KeyError` if there is no child with the given name.
        """
        if not self._remove(name):
            raise KeyError(name)

    remove = __delitem__

    def pop(self, name, default=_marker):
        objref = self._remove(name)
        if not objref:
            if default is _marker:
                raise KeyError(name)
            return default

        type, obj = objref
        if obj:
            return obj
        return self._load(name, type, False)

    def _remove(self, name):
        contents = self._contents
        objref = contents.get(name)
        if objref:
            type, obj = objref
            if obj is _removed:
                return None
            contents[name] = (type, _removed)
            _set_dirty(self)
        return objref

    def _load(self, name, type, cache=True):
        if type == 'folder':
            fspath = resource_path(self, name, CHURRO_FOLDER)
        else:
            fspath = resource_path(self, name) + CHURRO_EXT
        obj = codec.decode(self._fs.open(fspath, DECODE_MODE))
        obj.__parent__ = self
        obj.__name__ = name
        obj._fs = self._fs
        obj._dirty = False
        if cache:
            self._contents[name] = (type, obj)
        return obj

    def _save(self, fs):
        self._fs = fs
        path = resource_path(self)
        if not fs.exists(path):
            fs.mkdir(path)
        for name, (type, obj) in self._contents.items():
            if obj is None:
                continue
            if type == 'folder':
                if obj is _removed:
                    fs.rmtree(resource_path(self, name))
                else:
                    obj._save(fs)
            else:
                fspath = resource_path(self, name) + CHURRO_EXT
                if obj is _removed:
                    fs.rm(fspath)
                else:
                    codec.encode(obj, fs.open(fspath, ENCODE_MODE))
                    obj._dirty = False
                    obj._fs = fs
        fspath = '%s/%s' % (path, CHURRO_FOLDER)
        codec.encode(self, fs.open(fspath, ENCODE_MODE))
        self._dirty = False

    #def __repr__(self):
    #    pass


class PersistentDict(DictWrapper, Persistent):
    """
    A `PersistentDict` is a Python `dict` work alike that marks its parent
    object as `dirty` whenever it is mutated, solving the problem of using
    mutable datastructures as values for persistent properties with `Churro`
    and eliminating the need to call :meth:`~churro.Persistent.set_dirty`
    in application code when updating the dictionary.
    """
    data = PersistentProperty()

    def mutated(self):
        self.set_dirty()

    def __setinstance__(self, instance):
        self.__instance__ = instance
        for obj in self.data.values():
            if isinstance(obj, Persistent):
                obj.__setinstance__(self.__instance__)

class PersistentList(ListWrapper, Persistent):
    """
    A `PersistentList` is a Python `dict` work alike that marks its parent
    object as `dirty` whenever it is mutated, solving the problem of using
    mutable datastructures as values for persistent properties with `Churro`
    and eliminating the need to call :meth:`~churro.Persistent.set_dirty`
    in application code when updating the list.
    """
    data = PersistentProperty()

    def mutated(self):
        self.set_dirty()

    def __setinstance__(self, instance):
        self.__instance__ = instance
        for obj in self.data:
            if isinstance(obj, Persistent):
                obj.__setinstance__(self.__instance__)


class _Session(object):
    closed = False
    root = None

    def __init__(self, fs):
        self.fs = fs
        transaction.get().join(self)

    def abort(self, tx):
        """
        Part of datamanager API.
        """
        self.close()

    tpc_abort = abort

    def tpc_begin(self, tx):
        """
        Part of datamanager API.
        """

    def commit(self, tx):
        """
        Part of datamanager API.
        """

    def tpc_vote(self, tx):
        """
        Part of datamanager API.
        """
        self.flush()

    def flush(self):
        root = self.root
        if root is None or not root._dirty:
            # Nothing to do
            return

        root._save(self.fs)

    def tpc_finish(self, tx):
        """
        Part of datamanager API.
        """

    def sortKey(self):
        return 'Churro'

    def close(self):
        self.closed = True

    def get_root(self, factory):
        if self.root is not None: # is not None
            return self.root

        fs = self.fs
        path = '/' + CHURRO_FOLDER
        if fs.exists(path):
            root = codec.decode(fs.open(path, DECODE_MODE))
            root._dirty = False
        else:
            root = factory()
        root._fs = fs
        root.__name__ = root.__parent__ = None
        self.root = root
        return root


def _resolve_dotted_name(name):
    names = name.split('.')
    path = names.pop(0)
    target = __import__(path)
    while names:
        segment = names.pop(0)
        path += '.' + segment
        try:
            target = getattr(target, segment)
        except AttributeError:
            __import__(path)
            target = getattr(target, segment)
    return target


def resource_path(obj, *elements):
    def _inner(obj, path):
        if obj.__parent__ is not None:
            _inner(obj.__parent__, path)
            path.append(obj.__name__)
        return path
    path = _inner(obj, [])
    if elements:
        path.extend(elements)
    return '/' + '/'.join(path)


def _set_dirty(obj):
    while obj is not None:
        obj._dirty = True
        obj = obj.__parent__



