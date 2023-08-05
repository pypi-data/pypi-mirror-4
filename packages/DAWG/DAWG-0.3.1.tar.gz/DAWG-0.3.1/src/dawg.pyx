# cython: profile=True
from __future__ import unicode_literals
from libcpp.string cimport string
cimport cython
from cpython.sequence cimport PySequence_InPlaceConcat

from iostream cimport stringstream, istream, ostream, ifstream
cimport iostream

cimport _dawg
from _dawg_builder cimport DawgBuilder
from _dictionary cimport Dictionary
from _guide cimport Guide
from _completer cimport Completer
from _base_types cimport BaseType, SizeType
cimport _guide_builder
cimport _dictionary_builder
cimport b64_decode

import collections
import struct
import sys
from binascii import b2a_base64

cdef class DAWG:
    """
    Base DAWG wrapper.
    """
    cdef Dictionary dct
    cdef _dawg.Dawg dawg

    def __dealloc__(self):
        self.dct.Clear()
        self.dawg.Clear()

    def __init__(self, arg=None, input_is_sorted=False):
        if arg is None:
            arg = []
        if not input_is_sorted:
            arg = sorted(arg)
        self._build_from_iterable(arg)


    def _build_from_iterable(self, iterable):
        cdef DawgBuilder dawg_builder

        cdef bytes b_key
        for key in iterable:
            if isinstance(key, unicode):
                b_key = key.encode('utf8')
            else:
                b_key = key
            dawg_builder.Insert(b_key)

        dawg_builder.Finish(&self.dawg)
        _dictionary_builder.Build(self.dawg, &(self.dct))

    def __contains__(self, key):
        if isinstance(key, unicode):
            return self.has_key(key)
        return self.b_has_key(key)

    cpdef bint has_key(self, unicode key) except -1:
        cdef bytes b_key = key.encode('utf8')
        return self.b_has_key(b_key)

    cpdef bint b_has_key(self, bytes key) except -1:
        return self.dct.Contains(key)

    cpdef bytes tobytes(self):
        """
        Returns raw DAWG content as bytes.
        """
        cdef stringstream stream
        self.dct.Write(<ostream *> &stream)
        cdef bytes res = stream.str()
        return res

    cpdef frombytes(self, bytes data):
        """
        Loads DAWG from bytes ``data``.

        FIXME: it seems there is a memory leak here (DAWG uses 3x memory
        when loaded using ``.frombytes`` compared to DAWG loaded
        using ``.load``).
        """
        cdef string s_data = data
        cdef stringstream* stream = new stringstream(s_data)

        try:
            res = self.dct.Read(<istream *> stream)

            if not res:
                self.dct.Clear()
                raise IOError("Invalid data format")

            return self
        finally:
            del stream

    def read(self, f):
        """
        Loads DAWG from a file-like object.

        FIXME: this method should'n read the whole stream.
        """
        self.frombytes(f.read())

    def write(self, f):
        """
        Writes DAWG to a file-like object.
        """
        f.write(self.tobytes())

    def load(self, path):
        """
        Loads DAWG from a file.
        """
        if isinstance(path, unicode):
            path = path.encode(sys.getfilesystemencoding())

        cdef ifstream stream
        stream.open(path, iostream.binary)

        res = self.dct.Read(<istream*> &stream)

        stream.close()

        if not res:
            self.dct.Clear()
            raise IOError("Invalid data format")

        return self


    def save(self, path):
        """
        Saves DAWG to a file.
        """
        with open(path, 'wb') as f:
            self.write(f)

    # pickling support
    def __reduce__(self):
        return self.__class__, tuple(), self.tobytes()

    def __setstate__(self, state):
        self.frombytes(state)

    # half-internal methods
    def _size(self):
        return self.dct.size()

    def _total_size(self):
        return self.dct.total_size()

    def _file_size(self):
        return self.dct.file_size()

    cdef bint _has_value(self, BaseType index):
        return  self.dct.has_value(index)

    cdef list _similar_keys(self, unicode current_prefix, unicode key, BaseType cur_index, dict replace_chars):
        cdef BaseType next_index, index = cur_index
        cdef unicode prefix, u_replace_char, found_key
        cdef bytes b_step, b_replace_char
        cdef list res = []
        cdef list extra_keys

        cdef int start_pos = len(current_prefix)
        cdef int end_pos = len(key)
        cdef int word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                if self.dct.Follow(b_replace_char, &next_index):
                    prefix = current_prefix + key[start_pos:word_pos] + u_replace_char
                    extra_keys = self._similar_keys(prefix, key, next_index, replace_chars)
                    PySequence_InPlaceConcat(res, extra_keys)

            if not self.dct.Follow(b_step, &index):
                break
            word_pos += 1

        else:
            if self._has_value(index):
                found_key = current_prefix + key[start_pos:]
                res.insert(0, found_key)

        return res

    cpdef list similar_keys(self, unicode key, dict replaces):
        """
        Returns all variants of ``key`` in this DAWG according to
        ``replaces``.

        ``replaces`` is an object obtained from
        ``DAWG.compile_replaces(mapping)`` where mapping is a dict
        that maps single-char unicode sitrings to another single-char
        unicode strings.

        This may be useful e.g. for handling single-character umlauts.
        """
        return self._similar_keys("", key, self.dct.root(), replaces)

    @classmethod
    def compile_replaces(cls, dict replaces):

        for k,v in replaces.items():
            if len(k) != 1 or len(v) != 1:
                raise ValueError("Keys and values must be single-char unicode strings.")

        return dict(
            (
                k.encode('utf8'),
                (v.encode('utf8'), v)
            )
            for k, v in replaces.items()
        )


cdef class CompletionDAWG(DAWG):
    """
    DAWG with key completion support.
    """
    cdef Guide guide
    cdef Completer* completer

    def __init__(self, arg=None, input_is_sorted=False):
        super(CompletionDAWG, self).__init__(arg, input_is_sorted)
        if not _guide_builder.Build(self.dawg, self.dct, &self.guide):
            raise Exception("Error building completion information")
        if not self.completer:
            self.completer = new Completer(self.dct, self.guide)


    def __dealloc__(self):
        self.guide.Clear()
        del self.completer

    cpdef list keys(self, unicode prefix=""):
        cdef bytes b_prefix = prefix.encode('utf8')
        cdef unicode key
        cdef BaseType index = self.dct.root()
        cdef list res = []

        if not self.dct.Follow(b_prefix, &index):
            return res

        self.completer.Start(index, b_prefix)
        while self.completer.Next():
            key = (<char*>self.completer.key()).decode('utf8')
            res.append(key)

        return res

    cpdef bytes tobytes(self) except +:
        """
        Returns raw DAWG content as bytes.
        """
        cdef stringstream stream
        self.dct.Write(<ostream *> &stream)
        self.guide.Write(<ostream *> &stream)
        cdef bytes res = stream.str()
        return res

    cpdef frombytes(self, bytes data):
        """
        Loads DAWG from bytes ``data``.

        FIXME: it seems there is memory leak here (DAWG uses 3x memory when
        loaded using frombytes vs load).
        """
        cdef char* c_data = data
        cdef stringstream stream
        stream.write(c_data, len(data))
        stream.seekg(0)

        res = self.dct.Read(<istream*> &stream)
        if not res:
            self.dct.Clear()
            raise IOError("Invalid data format: can't load _dawg.Dictionary")

        res = self.guide.Read(<istream*> &stream)
        if not res:
            self.guide.Clear()
            self.dct.Clear()
            raise IOError("Invalid data format: can't load _dawg.Guide")

        if self.completer:
            del self.completer
        self.completer = new Completer(self.dct, self.guide)

        return self


    def load(self, path):
        """
        Loads DAWG from a file.
        """
        if isinstance(path, unicode):
            path = path.encode(sys.getfilesystemencoding())

        cdef ifstream stream
        stream.open(path, iostream.binary)

        try:
            res = self.dct.Read(<istream*> &stream)
            if not res:
                self.dct.Clear()
                raise IOError("Invalid data format: can't load _dawg.Dictionary")

            res = self.guide.Read(<istream*> &stream)
            if not res:
                self.guide.Clear()
                self.dct.Clear()
                raise IOError("Invalid data format: can't load _dawg.Guide")

            if self.completer:
                del self.completer
            self.completer = new Completer(self.dct, self.guide)

        finally:
            stream.close()

        return self

    def _transitions(self):
        transitions = set()
        cdef BaseType index, prev_index, completer_index
        cdef char* key

        self.completer.Start(self.dct.root())
        while self.completer.Next():
            key = <char*>self.completer.key()

            index = self.dct.root()

            for i in range(self.completer.length()):
                prev_index = index
                self.dct.Follow(&(key[i]), 1, &index)
                transitions.add(
                    (prev_index, <unsigned char>key[i], index)
                )

        return sorted(list(transitions))


# This symbol is not allowed in utf8 so it is safe to use
# as a separator between utf8-encoded string and binary payload.
DEF PAYLOAD_SEPARATOR = b'\xff'
DEF MAX_VALUE_SIZE = 32768

cdef class BytesDAWG(CompletionDAWG):
    """
    DAWG that is able to transparently store extra binary payload in keys;
    there may be several payloads for the same key.

    In other words, this class implements read-only DAWG-based
    {unicode -> list of bytes objects} mapping.
    """

    def __init__(self, arg=None, input_is_sorted=False):
        """
        ``arg`` must be an iterable of tuples (unicode_key, bytes_payload).
        """
        if arg is None:
            arg = []

        keys = (self._raw_key(d[0], d[1]) for d in arg)

        super(BytesDAWG, self).__init__(keys, input_is_sorted)


    cpdef bytes _raw_key(self, unicode key, bytes payload):
        cdef bytes encoded_payload = b2a_base64(payload)
        return key.encode('utf8') + PAYLOAD_SEPARATOR + encoded_payload

    cpdef bint b_has_key(self, bytes key) except -1:
        cdef BaseType index
        return self._follow_key(key, &index)

    def __getitem__(self, key):
        cdef list res = self.get(key)
        if res is None:
            raise KeyError(key)
        return res

    cpdef get(self, key, default=None):
        """
        Returns a list of payloads (as byte objects) for a given key
        or ``default`` if the key is not found.
        """
        cdef list res

        if isinstance(key, unicode):
            res = self.get_value(key)
        else:
            res = self.b_get_value(key)

        if not res:
            return default
        return res

    cdef bint _follow_key(self, bytes key, BaseType* index):
        index[0] = self.dct.root()
        if not self.dct.Follow(key, len(key), index):
            return False
        return self.dct.Follow(PAYLOAD_SEPARATOR, index)

    cpdef list get_value(self, unicode key):
        cdef bytes b_key = key.encode('utf8')
        return self.b_get_value(b_key)

    cdef list _value_for_index(self, BaseType index):
        cdef list res = []
        cdef int _len
        cdef b64_decode.decoder _b64_decoder
        cdef char[MAX_VALUE_SIZE] _b64_decoder_storage
        cdef bytes payload

        self.completer.Start(index)
        while self.completer.Next():
            _b64_decoder.init()
            _len = _b64_decoder.decode(
                self.completer.key(),
                self.completer.length(),
                _b64_decoder_storage
            )
            payload = _b64_decoder_storage[:_len]
            res.append(payload)

        return res

    cpdef list b_get_value(self, bytes key):
        cdef BaseType index
        if not self._follow_key(key, &index):
            return []
        return self._value_for_index(index)


    cpdef list items(self, unicode prefix=""):
        cdef bytes b_prefix = prefix.encode('utf8')
        cdef bytes value, b_value
        cdef unicode u_key
        cdef int i
        cdef list res = []
        cdef char* raw_key
        cdef char* raw_value
        cdef int raw_value_len

        cdef BaseType index = self.dct.root()
        if not self.dct.Follow(b_prefix, &index):
            return res

        cdef int _len
        cdef b64_decode.decoder _b64_decoder
        cdef char[MAX_VALUE_SIZE] _b64_decoder_storage

        self.completer.Start(index, b_prefix)
        while self.completer.Next():
            raw_key = <char*>self.completer.key()

            for i in range(0, self.completer.length()):
                if raw_key[i] == PAYLOAD_SEPARATOR:
                    break

            raw_value = &(raw_key[i])
            raw_value_len = self.completer.length() - i

            _b64_decoder.init()
            _len = _b64_decoder.decode(raw_value, raw_value_len, _b64_decoder_storage)
            value = _b64_decoder_storage[:_len]

            u_key = raw_key[:i].decode('utf8')
            res.append(
                (u_key, value)
            )

        return res

    cpdef list keys(self, unicode prefix=""):
        cdef bytes b_prefix = prefix.encode('utf8')
        cdef unicode u_key
        cdef int i
        cdef list res = []
        cdef char* raw_key

        cdef BaseType index = self.dct.root()
        if not self.dct.Follow(b_prefix, &index):
            return res

        self.completer.Start(index, b_prefix)
        while self.completer.Next():
            raw_key = <char*>self.completer.key()

            for i in range(0, self.completer.length()):
                if raw_key[i] == PAYLOAD_SEPARATOR:
                    break

            u_key = raw_key[:i].decode('utf8')
            res.append(u_key)
        return res

    cdef bint _has_value(self, BaseType index):
        cdef BaseType _index = index
        return self.dct.Follow(PAYLOAD_SEPARATOR, &_index)

    cdef list _similar_items(self, unicode current_prefix, unicode key, BaseType cur_index, dict replace_chars):
        cdef BaseType next_index, index = cur_index
        cdef unicode prefix, u_replace_char, found_key
        cdef bytes b_step, b_replace_char
        cdef list res = []
        cdef list extra_items, value

        cdef int start_pos = len(current_prefix)
        cdef int end_pos = len(key)
        cdef int word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                if self.dct.Follow(b_replace_char, &next_index):
                    prefix = current_prefix + key[start_pos:word_pos] + u_replace_char
                    extra_items = self._similar_items(prefix, key, next_index, replace_chars)
                    PySequence_InPlaceConcat(res, extra_items)

            if not self.dct.Follow(b_step, &index):
                break
            word_pos += 1

        else:
            if self.dct.Follow(PAYLOAD_SEPARATOR, &index):
                found_key = current_prefix + key[start_pos:]
                value = self._value_for_index(index)
                res.insert(0, (found_key, value))

        return res

    cpdef list similar_items(self, unicode key, dict replaces):
        """
        Returns a list of (key, value) tuples for all variants of ``key``
        in this DAWG according to ``replaces``.

        ``replaces`` is an object obtained from
        ``DAWG.compile_replaces(mapping)`` where mapping is a dict
        that maps single-char unicode sitrings to another single-char
        unicode strings.
        """
        return self._similar_items("", key, self.dct.root(), replaces)

    cdef list _similar_item_values(self, int start_pos, unicode key, BaseType cur_index, dict replace_chars):
        cdef BaseType next_index, index = cur_index
        cdef unicode prefix, u_replace_char, found_key
        cdef bytes b_step, b_replace_char
        cdef list res = []
        cdef list extra_items, value

        #cdef int start_pos = len(current_prefix)
        cdef int end_pos = len(key)
        cdef int word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                if self.dct.Follow(b_replace_char, &next_index):
                    extra_items = self._similar_item_values(word_pos+1, key, next_index, replace_chars)
                    PySequence_InPlaceConcat(res, extra_items)

            if not self.dct.Follow(b_step, &index):
                break
            word_pos += 1

        else:
            if self.dct.Follow(PAYLOAD_SEPARATOR, &index):
                value = self._value_for_index(index)
                res.insert(0, value)

        return res

    cpdef list similar_item_values(self, unicode key, dict replaces):
        """
        Returns a list of values for all variants of the ``key``
        in this DAWG according to ``replaces``.

        ``replaces`` is an object obtained from
        ``DAWG.compile_replaces(mapping)`` where mapping is a dict
        that maps single-char unicode sitrings to another single-char
        unicode strings.
        """
        return self._similar_item_values(0, key, self.dct.root(), replaces)



cdef class RecordDAWG(BytesDAWG):
    """
    DAWG that is able to transparently store binary payload in keys;
    there may be several payloads for the same key.

    The payload format must be defined at creation time using ``fmt``
    constructor argument; it has the same meaning as ``fmt`` argument
    for functions from ``struct`` module; take a look at
    http://docs.python.org/library/struct.html#format-strings for the
    specification.

    In other words, this class implements read-only DAWG-based
    {unicode -> list of tuples} mapping where all tuples are of the
    same structure an may be packed with the same format string.
    """
    cdef _struct

    def __init__(self, fmt, arg=None, input_is_sorted=False):
        """
        ``arg`` must be an iterable of tuples (unicode_key, data_tuple).
        data tuples will be converted to bytes with
        ``struct.pack(fmt, *data_tuple)``.

        Take a look at
        http://docs.python.org/library/struct.html#format-strings for the
        format string specification.
        """
        self._struct = struct.Struct(str(fmt))

        if arg is None:
            arg = []

        keys = ((d[0], self._struct.pack(*d[1])) for d in arg)
        super(RecordDAWG, self).__init__(keys, input_is_sorted)

    cdef list _value_for_index(self, BaseType index):
        cdef list value = BytesDAWG._value_for_index(self, index)
        return [self._struct.unpack(val) for val in value]

    cpdef list items(self, unicode prefix=""):
        cdef list items = BytesDAWG.items(self, prefix)
        return [(key, self._struct.unpack(val)) for (key, val) in items]


cdef class IntDAWG(DAWG):
    """
    Dict-like class based on DAWG.
    It can store integer values for unicode keys.
    """
    def __init__(self, arg=None, input_is_sorted=False):
        """
        ``arg`` must be an iterable of tuples (unicode_key, int_value)
        or a dict {unicode_key: int_value}.
        """
        if arg is None:
            arg = []

        if isinstance(arg, collections.Mapping):
            iterable = ((key, arg[key]) for key in arg)
        else:
            iterable = arg

        super(IntDAWG, self).__init__(iterable, input_is_sorted)


    def _build_from_iterable(self, iterable):
        cdef DawgBuilder dawg_builder

        cdef bytes b_key
        for key, value in iterable:
            if value < 0:
                raise ValueError("Negative values are not supported")
            b_key = key.encode('utf8')
            dawg_builder.Insert(b_key, value)

        cdef _dawg.Dawg dawg
        dawg_builder.Finish(&dawg)
        _dictionary_builder.Build(dawg, &(self.dct))

    def __getitem__(self, key):
        cdef int res = self.get(key, -1)
        if res == -1:
            raise KeyError(key)
        return res

    cpdef get(self, key, default=None):
        """
        Returns a list of payloads (as byte objects) for a given key
        or ``default`` if the key is not found.
        """
        cdef int res

        if isinstance(key, unicode):
            res = self.get_value(key)
        else:
            res = self.b_get_value(key)

        if res == -1:
            return default
        return res

    cpdef int get_value(self, unicode key):
        cdef bytes b_key = key.encode('utf8')
        return self.dct.Find(b_key)

    cpdef int b_get_value(self, bytes key):
        return self.dct.Find(key)
