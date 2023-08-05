# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import struct
from binascii import a2b_base64

from . import wrapper

class DAWG(object):
    """
    Base DAWG wrapper.
    """
    def __init__(self):
        self.dct = None

    def __contains__(self, key):
        if not isinstance(key, bytes):
            key = key.encode('utf8')
        return self.dct.contains(key)

    def load(self, path):
        """
        Loads DAWG from a file.
        """
        self.dct = wrapper.Dictionary.load(path)
        return self

    def _has_value(self, index):
        return self.dct.has_value(index)

    def _similar_keys(self, current_prefix, key, index, replace_chars):

        res = []
        start_pos = len(current_prefix)
        end_pos = len(key)
        word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                next_index = self.dct.follow_bytes(b_replace_char, next_index)

                if next_index is not None:
                    prefix = current_prefix + key[start_pos:word_pos] + u_replace_char
                    extra_keys = self._similar_keys(prefix, key, next_index, replace_chars)
                    res += extra_keys

            index = self.dct.follow_bytes(b_step, index)
            if index is None:
                break
            word_pos += 1

        else:
            if self._has_value(index):
                found_key = current_prefix + key[start_pos:]
                res.insert(0, found_key)

        return res

    def similar_keys(self, key, replaces):
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
    def compile_replaces(cls, replaces):

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


class CompletionDAWG(DAWG):
    """
    DAWG with key completion support.
    """

    def __init__(self):
        super(CompletionDAWG, self).__init__()
        self.guide = None
        self.completer = None

    def keys(self, prefix=""):
        b_prefix = prefix.encode('utf8')
        index = self.dct.root()
        res = []

        index = self.dct.follow_bytes(b_prefix, index)
        if index is None:
            return res

        self.completer.start(index, b_prefix)

        while self.completer.next():
            key = self.completer.key.decode('utf8')
            res.append(key)

        return res

    def load(self, path):
        """
        Loads DAWG from a file.
        """
        self.dct = wrapper.Dictionary()
        self.guide = wrapper.Guide()

        with open(path, 'rb') as f:
            self.dct.read(f)
            self.guide.read(f)

        self.completer = wrapper.Completer(self.dct, self.guide)
        return self


# This symbol is not allowed in utf8 so it is safe to use
# as a separator between utf8-encoded string and binary payload.
PAYLOAD_SEPARATOR = b'\xff'
MAX_VALUE_SIZE = 32768

class BytesDAWG(CompletionDAWG):
    """
    DAWG that is able to transparently store extra binary payload in keys;
    there may be several payloads for the same key.

    In other words, this class implements read-only DAWG-based
    {unicode -> list of bytes objects} mapping.
    """

    def __contains__(self, key):
        if not isinstance(key, bytes):
            key = key.encode('utf8')
        return bool(self._follow_key(key))

#    def b_has_key(self, key):
#        return bool(self._follow_key(key))

    def __getitem__(self, key):
        res = self.get(key)
        if res is None:
            raise KeyError(key)
        return res

    def get(self, key, default=None):
        """
        Returns a list of payloads (as byte objects) for a given key
        or ``default`` if the key is not found.
        """
        if not isinstance(key, bytes):
            key = key.encode('utf8')

        return self.b_get_value(key) or default

    def _follow_key(self, b_key):
        index = self.dct.follow_bytes(b_key, self.dct.root())
        if not index:
            return False

        index = self.dct.follow_bytes(PAYLOAD_SEPARATOR, index)
        if not index:
            return False

        return index

    def _value_for_index(self, index):
        res = []

        self.completer.start(index)
        while self.completer.next():
            # a2b_base64 doesn't support bytearray in python 2.6
            # so it is converted (and copied) to bytes
            b64_data = bytes(self.completer.key)
            res.append(a2b_base64(b64_data))

        return res

    def b_get_value(self, b_key):
        index = self._follow_key(b_key)
        if not index:
            return []
        return self._value_for_index(index)

    def keys(self, prefix=""):
        if not isinstance(prefix, bytes):
            prefix = prefix.encode('utf8')
        res = []

        index = self.dct.root()

        if prefix:
            index = self.dct.follow_bytes(prefix, index)
            if not index:
                return res

        self.completer.start(index, prefix)
        while self.completer.next():
            payload_idx = self.completer.key.index(PAYLOAD_SEPARATOR)
            u_key = self.completer.key[:payload_idx].decode('utf8')
            res.append(u_key)
        return res

    def items(self, prefix=""):
        if not isinstance(prefix, bytes):
            prefix = prefix.encode('utf8')
        res = []

        index = self.dct.root()
        if prefix:
            index = self.dct.follow_bytes(prefix, index)
            if not index:
                return res

        self.completer.start(index, prefix)
        while self.completer.next():
            key, value = self.completer.key.split(PAYLOAD_SEPARATOR)
            res.append(
                (key.decode('utf8'), a2b_base64(bytes(value))) # python 2.6 fix
            )

        return res


    def _has_value(self, index):
        return self.dct.follow_bytes(PAYLOAD_SEPARATOR, index)

    def _similar_items(self, current_prefix, key, index, replace_chars):

        res = []
        start_pos = len(current_prefix)
        end_pos = len(key)
        word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                next_index = self.dct.follow_bytes(b_replace_char, next_index)
                if next_index:
                    prefix = current_prefix + key[start_pos:word_pos] + u_replace_char
                    extra_items = self._similar_items(prefix, key, next_index, replace_chars)
                    res += extra_items

            index = self.dct.follow_bytes(b_step, index)
            if not index:
                break
            word_pos += 1

        else:
            index = self.dct.follow_bytes(PAYLOAD_SEPARATOR, index)
            if index:
                found_key = current_prefix + key[start_pos:]
                value = self._value_for_index(index)
                res.insert(0, (found_key, value))

        return res

    def similar_items(self, key, replaces):
        """
        Returns a list of (key, value) tuples for all variants of ``key``
        in this DAWG according to ``replaces``.

        ``replaces`` is an object obtained from
        ``DAWG.compile_replaces(mapping)`` where mapping is a dict
        that maps single-char unicode sitrings to another single-char
        unicode strings.
        """
        return self._similar_items("", key, self.dct.root(), replaces)


    def _similar_item_values(self, start_pos, key, index, replace_chars):
        res = []
        end_pos = len(key)
        word_pos = start_pos

        while word_pos < end_pos:
            b_step = key[word_pos].encode('utf8')

            if b_step in replace_chars:
                next_index = index
                b_replace_char, u_replace_char = replace_chars[b_step]

                next_index = self.dct.follow_bytes(b_replace_char, next_index)
                if next_index:
                    extra_items = self._similar_item_values(word_pos+1, key, next_index, replace_chars)
                    res += extra_items

            index = self.dct.follow_bytes(b_step, index)
            if not index:
                break
            word_pos += 1

        else:
            index = self.dct.follow_bytes(PAYLOAD_SEPARATOR, index)
            if index:
                value = self._value_for_index(index)
                res.insert(0, value)

        return res

    def similar_item_values(self, key, replaces):
        """
        Returns a list of values for all variants of the ``key``
        in this DAWG according to ``replaces``.

        ``replaces`` is an object obtained from
        ``DAWG.compile_replaces(mapping)`` where mapping is a dict
        that maps single-char unicode sitrings to another single-char
        unicode strings.
        """
        return self._similar_item_values(0, key, self.dct.root(), replaces)


class RecordDAWG(BytesDAWG):
    def __init__(self, fmt):
        super(RecordDAWG, self).__init__()
        self._struct = struct.Struct(str(fmt))
        self.fmt = fmt

    def _value_for_index(self, index):
        value = super(RecordDAWG, self)._value_for_index(index)
        return [self._struct.unpack(val) for val in value]

    def items(self, prefix=""):
        res = super(RecordDAWG, self).items(prefix)
        return [(key, self._struct.unpack(val)) for (key, val) in res]

