# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt


class FixedWidthRecord(object):

    fields = ()
    LEFT = 'ljust'
    RIGHT = 'rjust'

    encoding = 'utf-8'
    lineterminator = '\r\n'

    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        result = ''
        for config in self.fields:
            name, length, fill, direction = self._expand_config(config)

            value = unicode(self.data.get(name, ''))
            value = value[:length]

            method = getattr(value, direction)
            result += method(length, fill)
        result += self.lineterminator
        return result.encode(self.encoding)

    @classmethod
    def _expand_config(cls, config):
        name = config[0]
        length = config[1]
        try:
            fill = config[2]
        except IndexError:
            fill = ' '
        try:
            direction = config[3]
        except IndexError:
            direction = cls.RIGHT
        return name, length, fill, direction

    @classmethod
    def parse_file(cls, file):
        config = [cls._expand_config(x) for x in cls.fields]
        result = []
        for line in file:
            result.append(cls.parse(line, config))
        return result

    @classmethod
    def parse(cls, line, config=None):
        assert line.endswith(cls.lineterminator)
        line = line.decode(cls.encoding)
        line = line.replace(cls.lineterminator, '', 1)
        record = cls()
        if config is None:
            config = [cls._expand_config(x) for x in cls.fields]

        for name, length, fill, direction in config:
            direction = direction.replace('just', 'strip')

            value = line[:length]
            method = getattr(cls, direction)
            record.data[name] = method(value, fill)

            line = line[length:]

        return record

    @staticmethod
    def lstrip(value, fill):
        return value.rstrip(fill)

    @staticmethod
    def rstrip(value, fill):
        return value.lstrip(fill)
