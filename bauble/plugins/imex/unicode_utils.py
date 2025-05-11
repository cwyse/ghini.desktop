import csv

import bauble.utils as utils


class UnicodeReader:

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.reader = csv.DictReader(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def __next__(self):
        row = next(self.reader)
        t = {}
        for k, v in row.items():
            if len(v) == 0:
                t[k] = None
            else:
                t[k] = utils.to_unicode(v, self.encoding)

        return t

    def __iter__(self):
        return self


class InvalidDataError(Exception):
    pass

# TODO: add support for exporting only specific tables
class UnicodeWriter:

    def __init__(
        self, f, fields=None, dialect=csv.excel, encoding="utf-8", **kwds
    ):
        self.writer = csv.writer(f, dialect=dialect, **kwds)
        self.field_order = fields
        self.encoding = encoding

    def writerow(self, row):
        if isinstance(row, dict):
            row = [row[k] for k in self.field_order]
        t = [utils.to_unicode(s, self.encoding) for s in row]
        self.writer.writerow(t)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

