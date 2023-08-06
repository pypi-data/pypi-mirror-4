#!/usr/bin/env python
# coding: utf-8

import csv
from StringIO import StringIO


DELIMITER = ','
QUOTE_CHAR = '"'
LINE_TERMINATOR = '\n'

class MyCSV(csv.Dialect):
    doublequote = True
    skipinitialspace = False
    quoting = csv.QUOTE_ALL

def read(table, file_name_or_pointer, convert_types=True, delimiter=DELIMITER,
         quote_char=QUOTE_CHAR, line_terminator=LINE_TERMINATOR):
    MyCSV.delimiter = delimiter
    MyCSV.quotechar = quote_char
    MyCSV.lineterminator = line_terminator
    table.convert_types = convert_types
    if isinstance(file_name_or_pointer, (str, unicode)):
        table.csv_filename = file_name_or_pointer
        fp = open(file_name_or_pointer, 'r')
    else:
        fp = file_name_or_pointer
    info = fp.read().decode(table.input_encoding).encode('utf8')
    reader = csv.reader(info.split('\n'), dialect=MyCSV)
    table.data = [x for x in reader if x]
    if table.csv_filename:
        fp.close()
    table.headers = []
    if table.data:
        table.headers = [x.decode('utf8') for x in table.data[0]]
        table.extend([[y.decode('utf8') for y in x] for x in table.data[1:]])
        if table.convert_types:
            table.normalize_types()

def write(table, filename_or_pointer=None, delimiter=DELIMITER,
          quote_char=QUOTE_CHAR, line_terminator=LINE_TERMINATOR):
    MyCSV.delimiter = delimiter
    MyCSV.quotechar = quote_char
    MyCSV.lineterminator = line_terminator
    table.decode()
    table.encode()
    if filename_or_pointer is not None:
        if isinstance(filename_or_pointer, (str, unicode)):
            fp = open(filename_or_pointer, 'w')
            close = True
        else:
            fp = filename_or_pointer
            close = False
    else:
        fp = StringIO()
    writer = csv.writer(fp, dialect=MyCSV)
    writer.writerow(table.headers)
    writer.writerows(table)
    table.decode(table.output_encoding)
    if filename_or_pointer is None:
        contents = fp.getvalue()
        fp.close()
        return contents
    elif close:
        fp.close()
