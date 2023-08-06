# coding: utf-8
import sys
import os
import argparse
from storage import Storage


storage = Storage()


def list_labels():
    labels = storage.get_all()
    for label, path in labels.iteritems():
        print label, '\t\t', path


def remove(label):
    try:
        storage.remove(label)
        print '%s label was removed.' % label
    except:
        sys.stderr.write('%s is not a valid label.\n' % label)
        sys.exit(1)


def replace(label, path):
    try:
        storage.replace(label, path)
        print '%s label now points to %s.' % (label, path)
    except:
        sys.stderr.write('%s is not a valid label.\n' % label)
        sys.exit(1)


def add(label, path):
    try:
        storage.add(label, path)
        print '%s label points to %s.' % (label, path)
    except:
        sys.stderr.write('%s label already exists. Use --replace.\n' % label)
        sys.exit(1)


def main():
    """Entrypoint for the `label` utility."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--remove', action='store_true', help='remove an existing label')
    group.add_argument('--replace', action='store_true', help='replace an existing label')
    parser.add_argument('label', help='name of the label')

    args = parser.parse_args()

    curr_dir = os.getcwd()
    storage.open_or_create()

    #if args.list:           #FIXME insert this argument [and s/if/elif in next case]
    #    list_labels()

    if args.remove:
        remove(args.label)

    elif args.replace:
        replace(args.label, curr_dir)

    else:
        add(args.label, curr_dir)