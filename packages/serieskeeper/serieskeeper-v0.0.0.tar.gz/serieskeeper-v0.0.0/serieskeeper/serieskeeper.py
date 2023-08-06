import data
import argparse
from os.path import expanduser
import sys


def print_results(results):
    for line in results:
        print line

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', help='add new series to collection',
            type=str, metavar='SERIES')
    group.add_argument('-m', '--mark',
            help='mark a series as finished or unfinished', type=str,
            metavar='SERIES')
    group.add_argument('-d', '--delete', help='remove a series from collection',
            type=str, metavar='SERIES')
    group.add_argument('-l', '--list', help='list all series in collection',
            action="store_true")
    group.add_argument('-u', '--unread',
            help='list unfinished series in collection', action="store_true")
    group.add_argument('-r', '--read', help='list finished series in collection',
            action="store_true")
    group.add_argument('-c', '--create', help='create a new collection',
            action="store_true")
    parser.add_argument('-f', '--file', help='path to collection file',
            type=str, metavar='FILE')
    args = parser.parse_args()
    
    if args.file:
        file_path = args.file
    else:
        file_path = expanduser('~') + '/.collection'
    
    if args.list:
        data.collection = data.get_collection(file_path)
        results = data.list_series(args.list, data.collection, 'all')
        print_results(results)
    elif args.unread:
        data.collection = data.get_collection(file_path)
        results = data.list_series(args.unread, data.collection, 'unread')
        print_results(results)
    elif args.read:
        data.collection = data.get_collection(file_path)
        results = data.list_series(args.read, data.collection, 'read')
        print_results(results)
    elif args.add:
        data.collection = data.get_collection(file_path)
        data.add_series(args.add, data.collection, file_path)
    elif args.mark:
        data.collection = data.get_collection(file_path)
        data.mark_series(args.mark, data.collection, file_path)
    elif args.delete:
        data.collection = data.get_collection(file_path)
        data.delete_series(args.delete, data.collection, file_path)
    elif args.create:
        try:
            data.create_collection(file_path)
        except data.ConflictError:
            sys.exit('sk: cannot create collection: File already exists')
    else:
        parser.print_help()
