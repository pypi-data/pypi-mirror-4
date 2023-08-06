# Based on Lib/shelve.py rev dd341e1e30a7

"""Manage shelves of serialised objects.

A "shelf" is a persistent, dictionary-like object.  The difference
with dbm databases is that the values (not the keys!) in a shelf can
be more complex Python objects -- before they are stored to disk, they will be
serialised using a configurable serialisation protocol. The keys are ordinary
strings.Currently, the following protocols are supported:

- The "pickle" protocol uses Python's "pickle" module to store essentially
  arbitrary Python objects. This includes most class instances, recursive data
  types, and objects containing lots of shared sub-objects. The downside is that
  the deserialisation is not safe -- it may execute arbitrary Python code. For
  more information, see the "pickle" module documentation.

  "pickle" supports one additional parameter:

  * protocol: Specifies the pickle protocol to use. See the "pickle" module
    documentation for more information. The default is currently 3.

- The "json" protocol serialises data to the JSON format. While it supports a
  narrower range of objects than pickle by default (JSON has notations for
  dicts, lists, numbers, strings, bools and None) it is also not inherently
  unsafe; the deserialisation process won't execute arbitrary code.

  "json" supports these additional parameters:

  * json_encoder_options: A dict of keyword arguments that will be passed to
    "json.dumps". These options can be used to customise the serialisation
    process. See the "json" module documentation for more information.
  * json_decoder_options: A dict of keyword arguments that will be passed to
    "json.loads". These options can be used to customise the deserialisation
    process. See the "json" module documentation for more information.
  * valueencoding: Since the "json" module produces str objects (i.e. unicode
    strings), this encoding will be used to turn these strings into bytes
    instances for storage. Default is UTF-8.

The default serialisation protocol is currently "pickle". More protocols may be
added in the future. To implement a custom serialiser, it is necessary to create
a mixin class that implements the "_load" and "_store" methods as documented in
"AbstractShelf" and then add this class to the module-level
"serialisation_protocols" dict.

To summarize the interface (key is a string, data is an arbitrary
object):

        import shelve2
        # open, with (g)dbm filename -- no suffix; other protocols may be
        # selected here.
        d = shelve2.open2(filename, protocol="pickle")

        d[key] = data   # store data at key (overwrites old data if
                        # using an existing key)
        data = d[key]   # retrieve a COPY of the data at key (raise
                        # KeyError if no such key) -- NOTE that this
                        # access returns a *copy* of the entry!
        del d[key]      # delete data stored at key (raises KeyError
                        # if no such key)
        flag = key in d # true if the key exists
        list = d.keys() # a list of all existing keys (slow!)

        d.close()       # close it

Dependent on the implementation, closing a persistent dictionary may
or may not be necessary to flush changes to disk.

Normally, d[key] returns a COPY of the entry.  This needs care when
mutable entries are mutated: for example, if d[key] is a list,
        d[key].append(anitem)
does NOT modify the entry d[key] itself, as stored in the persistent
mapping -- it only modifies the copy, which is then immediately
discarded, so that the append has NO effect whatsoever.  To append an
item to d[key] in a way that will affect the persistent mapping, use:
        data = d[key]
        data.append(anitem)
        d[key] = data

To avoid the problem with mutable entries, you may pass the keyword
argument writeback=True in the call to shelve.open.  When you use:
        d = shelve.open(filename, writeback=True)
then d keeps a cache of all entries you access, and writes them all back
to the persistent mapping when you call d.close().  This ensures that
such usage as d[key].append(anitem) works as intended.

However, using keyword argument writeback=True may consume vast amount
of memory for the cache, and it may make d.close() very slow, if you
access many of d's entries after opening it in this way: d has no way to
check which of the entries you access are mutable and/or which ones you
actually mutate, so it must cache, and write back at close, all of the
entries that you access.  You can call d.sync() to write back all the
entries in the cache, and empty the cache (d.sync() also synchronizes
the persistent dictionary on disk, if feasible).
"""

import abc
import collections
import json
import pickle

__all__ = [
    "Shelf", "BsdDbShelf", "DbfilenameShelf", "open",
    "AbstractShelf", "AbstractBsdDbShelf", "AbstractDbfilenameShelf",
    "PickleMixin", "JsonMixin", "open2"
]

class _ClosedDict(collections.MutableMapping):
    'Marker for a closed dict.  Access attempts raise a ValueError.'

    def closed(self, *args):
        raise ValueError('invalid operation on closed shelf')
    __iter__ = __len__ = __getitem__ = __setitem__ = __delitem__ = keys = closed

    def __repr__(self):
        return '<Closed Dictionary>'


class AbstractShelf(collections.MutableMapping, metaclass=abc.ABCMeta):
    """Base class for shelf implementations.

    This is initialized with a dictionary-like object.
    See the module's __doc__ string for an overview of the interface.

    This class cannot be instantiated directly because it uses the abstract
    "_dump" and "_load" methods to serialise and deserialise the objects passed
    to it. These methods need to be implemented in a subclass or supplied using
    a mixin class.
    """

    def __init__(self, dict, writeback=False, keyencoding="utf-8"):
        self.dict = dict
        self.writeback = writeback
        self.cache = {}
        self.keyencoding = keyencoding

    @abc.abstractmethod
    def _load(self, bytesvalue):
        """Decode the given byte string into a complex value.

        If decoding is not possible, an exception should be raised."""
        raise NotImplementedError

    @abc.abstractmethod
    def _dump(self, value):
        """Serialise the given value into a byte string.

        If the given value can not be serialised, an exception should be raised.
        """
        raise NotImplementedError

    def __iter__(self):
        for k in self.dict.keys():
            yield k.decode(self.keyencoding)

    def __len__(self):
        return len(self.dict)

    def __contains__(self, key):
        return key.encode(self.keyencoding) in self.dict

    def get(self, key, default=None):
        if key.encode(self.keyencoding) in self.dict:
            return self[key]
        return default

    def __getitem__(self, key):
        try:
            value = self.cache[key]
        except KeyError:
            value = self._load(self.dict[key.encode(self.keyencoding)])
            if self.writeback:
                self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        if self.writeback:
            self.cache[key] = value
        self.dict[key.encode(self.keyencoding)] = self._dump(value)

    def __delitem__(self, key):
        del self.dict[key.encode(self.keyencoding)]
        try:
            del self.cache[key]
        except KeyError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.sync()
        try:
            self.dict.close()
        except AttributeError:
            pass
        # Catch errors that may happen when close is called from __del__
        # because CPython is in interpreter shutdown.
        try:
            self.dict = _ClosedDict()
        except (NameError, TypeError):
            self.dict = None

    def __del__(self):
        if not hasattr(self, 'writeback'):
            # __init__ didn't succeed, so don't bother closing
            # see http://bugs.python.org/issue1339007 for details
            return
        self.close()

    def sync(self):
        if self.writeback and self.cache:
            self.writeback = False
            for key, entry in self.cache.items():
                self[key] = entry
            self.writeback = True
            self.cache = {}
        if hasattr(self.dict, 'sync'):
            self.dict.sync()


class AbstractBsdDbShelf(AbstractShelf):
    """Additional methods for shelf implementations using the "bsddb" interface.

    This adds methods first(), next(), previous(), last() and
    set_location() that have no counterpart in [g]dbm databases.

    The actual database must be opened using one of the "bsddb"
    modules "open" routines (i.e. bsddb.hashopen, bsddb.btopen or
    bsddb.rnopen) and passed to the constructor.

    See the module's __doc__ string for an overview of the interface.

    This class is abstract and needs implementations of the "_load" and "_store"
    methods to work. See "AbstractShelf" for more information.
    """

    def set_location(self, key):
        (key, value) = self.dict.set_location(key)
        return (key.decode(self.keyencoding), self._load(value))

    def next(self):
        (key, value) = next(self.dict)
        return (key.decode(self.keyencoding), self._load(value))

    def previous(self):
        (key, value) = self.dict.previous()
        return (key.decode(self.keyencoding), self._load(value))

    def first(self):
        (key, value) = self.dict.first()
        return (key.decode(self.keyencoding), self._load(value))

    def last(self):
        (key, value) = self.dict.last()
        return (key.decode(self.keyencoding), self._load(value))


class AbstractDbfilenameShelf(AbstractShelf):
    """Shelf implementation using the "dbm" generic dbm interface.

    This is initialized with the filename for the dbm database.
    See the module's __doc__ string for an overview of the interface.

    This class is abstract and needs implementations of the "_load" and "_store"
    methods to work. See "AbstractShelf" for more information.
    """

    def __init__(self, filename, flag='c', writeback=False,
                 keyencoding="utf-8"):
        import dbm
        Shelf.__init__(self, dbm.open(filename, flag), writeback, keyencoding)


# Pickle serialisation and old 'shelve' module interface.
class PickleMixin:
    """Serialisation implementation using the "pickle" module.

    This class is designed to be mixed into one of the Abstract*Shelf classes.
    """
    def __init__(self, protocol=None):
        if protocol is None:
            protocol = 3
        self._protocol = protocol

    def _load(self, bytesvalue):
        return pickle.loads(bytesvalue)

    def _dump(self, value):
        return pickle.dumps(value, protocol=self._protocol)


class Shelf(PickleMixin, AbstractShelf):
    """Implementation of "AbstractShelf" that uses the "pickle" module.

    This classed is provided for compatibility with the old "shelve" module.
    """
    def __init__(self, dict, protocol=None, writeback=False,
                 keyencoding="utf-8"):
        AbstractShelf.__init__(self, dict, writeback, keyencoding)
        PickleMixin.__init__(self, protocol)

class BsdDbShelf(PickleMixin, AbstractBsdDbShelf):
    """Implementation of "AbstractBsdDbShelf" that uses the "pickle" module.

    This classed is provided for compatibility with the old "shelve" module.
    """
    def __init__(self, dict, protocol=None, writeback=False,
                 keyencoding="utf-8"):
        AbstractBsdDbShelf.__init__(self, dict, writeback, keyencoding)
        PickleMixin.__init__(self, protocol)

class DbfilenameShelf(PickleMixin, AbstractDbfilenameShelf):
    """Implementation of "AbstractDbfilenameShelf" that uses "pickle".

    This classed is provided for compatibility with the old "shelve" module.
    """
    def __init__(self, filename, flag='c', protocol=None, writeback=False,
                 keyencoding="utf-8"):
        AbstractDbfilenameShelf.__init__(self, filename, flag, writeback,
                                         keyencoding)
        PickleMixin.__init__(self, protocol)

def open(filename, flag='c', protocol=None, writeback=False,
         keyencoding="utf-8"):
    """Open a persistent dictionary for reading and writing..

    This function only supports the "pickle" module for serialisation and is
    provided for compatibility with the old "shelve" interface. The "open2"
    function is recommended instead as it is able to support a wider range of
    serialisation protocols.

    The filename parameter is the base filename for the underlying
    database.  As a side-effect, an extension may be added to the
    filename and more than one file may be created.  The optional flag
    parameter has the same interpretation as the flag parameter of
    dbm.open(). The optional protocol parameter specifies the
    version of the pickle protocol (0, 1, or 2). The writeback parameter
    specifies whether the dictionary should cache any accessed values. The
    keyencoding parameter specifies the character encoding to use for dictionary
    keys, the default is UTF-8.

    See the module's __doc__ string for an overview of the interface.
    """
    return DbfilenameShelf(filename, flag, protocol, writeback, keyencoding)


# JSON serialisation.
class JsonMixin:
    """Serialisation implementation using JSON.

    Compared to pickle, JSON supports a far narrower range of Python objects by
    default. However, the representation is safe -- as in no arbitrary code can
    be executed during deserialisation -- and language-independent.
    """

    def __init__(self, json_encoder_options=None, json_decoder_options=None,
                 valueencoding="utf-8", ):
        """Initialise JsonMixin.

        "json_encoder_options" shall be a mapping, the contents of which will
        be passed to "json.dumps" as keyword arguments. Likewise for
        "json_decoder_options" and "json.loads".
        """
        if json_encoder_options is None:
            json_encoder_options = {}
        if json_decoder_options is None:
            json_decoder_options = {}
        self._encoder_options = json_encoder_options
        self._decoder_options = json_decoder_options
        self._valueencoding = valueencoding

    def _load(self, bytesvalue):
        return json.loads(bytesvalue.decode(self._valueencoding),
                          **self._decoder_options)

    def _dump(self, value):
        return json.dumps(value, **self._encoder_options).encode(
            self._valueencoding)


# Protocol-generic new interface.
serialisation_protocols = {
    "pickle": PickleMixin,
    "json": JsonMixin,
}

def get_mixin(protocol):
    """Get the mixin for that serialisation protocol."""
    try:
        mixin = serialisation_protocols[protocol]
    except KeyError:
        raise ValueError("unsupported serialisation protocol '%s'" % protocol)
    return mixin

def open2(filename, flag='c', serialisation_protocol="pickle", writeback=False,
          keyencoding="utf-8", *args, **kwargs):
    """Open a persistent dictionary for reading and writing.

    The filename parameter is the base filename for the underlying
    database.  As a side-effect, an extension may be added to the
    filename and more than one file may be created.  The optional flag
    parameter has the same interpretation as the flag parameter of
    dbm.open(). The optional serialisation_protocol parameter specifies the
    serialisation protocol to use; the default is "pickle", see the module
    __doc__ string for other options. The writeback parameter specifies whether
    the dictionary should cache any accessed values. The keyencoding parameter
    specifies the character encoding to use for dictionary keys, the default is
    UTF-8.

    Any additional (positional and keyword) arguments will be passed through to
    the serialisation implementation. See the relevant mixin class for more
    information on these.
    """
    mixin = get_mixin(serialisation_protocol)
    class DbfilenameShelfClass(mixin, AbstractDbfilenameShelf):
        def __init__(self, filename, flag='c', writeback=False,
                     keyencoding="utf-8", *args, **kwargs):
            AbstractDbfilenameShelf.__init__(self, filename, flag, writeback,
                                             keyencoding)
            mixin.__init__(self, *args, **kwargs)
    return DbfilenameShelfClass(filename, flag, writeback, keyencoding,
                                *args, **kwargs)
