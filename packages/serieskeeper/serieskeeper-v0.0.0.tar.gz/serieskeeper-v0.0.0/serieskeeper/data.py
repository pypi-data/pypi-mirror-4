#!/usr/bin/env python

import cPickle
import os


class ConflictError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Series(object):
    def __init__(self, title):
        self.title = title
        self.read = False


def create_collection(file_path):
    if os.path.exists(file_path):
        raise ConflictError('file already exists')
    else:
        collection = []
        write_out(file_path, collection)


def get_collection(file_path):
    f = open(file_path, 'rb')
    collection = cPickle.load(f)
    f.close()
    return collection


def write_out(file_path, data):
    f = open(file_path, 'wb')
    cPickle.dump(data, f)
    f.close()


def list_series(series, collection, style):
    results = []
    for series in collection:
        if series.read:
            status = "Read"
        else:
            status = "Unread"
        if style == 'all':
            results.append(status + '\t' + series.title)
        elif style == 'read' and status == 'Read':
            results.append(status + '\t' + series.title)
        elif style == 'unread' and status == 'Unread':
            results.append(status + '\t' + series.title)
    return results


def add_series(series, collection, file_path):
    collection.append(Series(series))
    write_out(file_path, collection)


def mark_series(series, collection, file_path):
    for item in collection:
        if item.title == series and item.read:
            item.read = False
        elif item.title == series and not item.read:
            item.read = True
        write_out(file_path, collection)


def delete_series(series, collection, file_path):
    series_list = []
    for item in collection:
        series_list.append(item.title)
    index = series_list.index(series)
    collection.pop(index)
    write_out(file_path, collection)
