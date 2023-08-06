import csv
import json
import StringIO

DEFAULT_JSON_INDENT_LEVEL = 4


class BaseFormatter(object):
    def start_format(self):
        return ''


    def format_record(self, record):
        pass


    def end_format(self):
        return ''


class CSVFormatter(BaseFormatter):
    def __init__(self, nvalues, header=None):
        self._nvalues = nvalues

        if header is not None:
            self._hvalues = self._read_line(header)
            if len(self._hvalues) != nvalues:
                raise ValueError("CSV formatter: number of header columns (%s) differs from number of data columns (%s)"\
                        % (len(self._hvalues), nvalues))
        else:
            self._hvalues = None


    def start_format(self):
        if self._hvalues is not None:
            return self._format_line(self._hvalues)
        else:
            return ''


    def format_record(self, strings):
        if len(strings) != self._nvalues:
            raise ValueError("The number of values to be formatted doesn't match the number of parsed values")

        return self._format_line(strings)


    def _format_line(self, values):
        out = StringIO.StringIO()

        writer = csv.writer(out)

        writer.writerow(map(lambda v: v.encode('utf-8'), values))

        line = out.getvalue()

        out.close()

        return line


    def _read_line(self, line):
        io = StringIO.StringIO(line)

        return csv.reader(io).next()


    def __str__(self):
        return 'CSVFormatter(%s)' % (self._nvalues,)


    __repr__ = __str__


class JSONFormatter(BaseFormatter):
    def __init__(self, keys, indent=False):
        self._keys = keys
        self._at_first = True
        if indent:
            self._indent = DEFAULT_JSON_INDENT_LEVEL
        else:
            self._indent = None


    def format_record(self, strings):
        if len(strings) != len(self._keys):
            raise ValueError("The number of values to be formatted doesn't match the number of parsed values")

        string = ''

        if self._at_first:
            self._at_first = False
            string += '\n'
        else:
            string += ',\n'

        d = dict(zip(self._keys, strings))

        string += json.dumps(d, indent=self._indent)

        return string


    def start_format(self):
        return '['


    def end_format(self):
        s = ''
        if not self._at_first:
            s += '\n'
        s += ']\n'

        return s


    def __str__(self):
        return 'JSONFormatter(%s)' % (', '.join(self._keys),)


class GeneralFormatter(BaseFormatter):
    def __init__(self, inter_strings):
        self._nformats = len(inter_strings) - 1
        # interleaving ...
        self._format = ''.join([x for pair in zip(inter_strings, ['%s'] * self._nformats + ['']) for x in pair])


    def format_record(self, values):
        if len(values) != self._nformats:
            raise ValueError("Invalid number of values. Expected %s, got %s" % (self._nformats, len(values)))

        return (self._format % tuple(values)) + '\n'


    def __str__(self):
        return 'GeneralFormatter(%s)' % (', '.join(self._keys),)


    __repr__ = __str__


