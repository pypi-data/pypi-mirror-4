# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict


class SeparatedRecord(UserDict.DictMixin):

    fields = 0
    encoding = 'utf-8'
    separator = ';'
    lineterminator = '\r\n'

    _RESERVED = [
        'fields', 'encoding', 'separator', 'lineterminator', 'key_names']

    def __init__(self, **data):
        self.data = dict()
        self._maxlen = dict()
        self.key_names = [''] * self.fields

        for name, key in self.__class__.__dict__.items():
            if name in self._RESERVED or name.startswith('_'):
                continue

            maxlen = None
            default = None
            if isinstance(key, tuple):
                if isinstance(key[1], int):
                    maxlen = key[1]
                    try:
                        default = key[2]
                    except IndexError:
                        pass
                else:
                    default = key[1]

                key = key[0]
                if default is not None:
                    self[key] = default
                if maxlen is not None:
                    self._maxlen[key] = maxlen
                setattr(self, name, key)
            if isinstance(key, int):
                # otherwise key might be a method defined on the class
                self.key_names[key-1] = name

        self.update(data)

    def __setitem__(self, key, value):
        self.data[self._map_key(key)] = value

    def __getitem__(self, key):
        key = self._map_key(key)
        return self._truncate(key, self.data.get(key, None))

    def keys(self):
        return range(1, self.fields+1)

    def has_key(self, key):
        return key in self.keys()

    def _str_key_names(self):
        "String representation of the key names, useable as headline."
        return self._str_values(self.key_names)

    def __str__(self):
        values = (self.__class__.escape(self[i] or '') for i in sorted(self))
        return self._str_values(values)

    def _str_values(self, values):
        str = unicode(self.separator).join(values)
        str = str.encode(self.encoding) + self.lineterminator
        return str

    def _truncate(self, key, text):
        if text is None:
            return None

        maxlen = self._maxlen.get(key, None)
        if maxlen is None:
            return text
        return text[:maxlen]

    def _map_key(self, key):
        if not isinstance(key, int):
            key = getattr(self, key)
        if key not in self:
            raise KeyError(key)
        return key

    @classmethod
    def escape(cls, text):
        return text

    @classmethod
    def unescape(cls, text):
        return text

    @classmethod
    def parse_file(cls, file):
        result = []
        for line in file:
            result.append(cls.parse(line))
        return result

    @classmethod
    def parse(cls, line):
        assert line.endswith(cls.lineterminator)
        line = line.decode(cls.encoding)
        line = line.replace(cls.lineterminator, '', 1)
        values = line.split(cls.separator)
        record = cls()
        for index, item in enumerate(values):
            record[index + 1] = cls.unescape(item)
        return record


class CSVRecord(SeparatedRecord):
    """Record which can be used to create a CSV-File."""

    @classmethod
    def escape(cls, text):
        return u'"%s"' % text.replace('"', '\'')

    @classmethod
    def unescape(cls, text):
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text
