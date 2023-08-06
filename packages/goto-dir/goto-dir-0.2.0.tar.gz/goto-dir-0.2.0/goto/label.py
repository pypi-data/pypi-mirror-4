# coding: utf-8
import sys
import os
import re
import locale
import argparse
from storage import Storage, LabelAlreadyExistsError, LabelTooLongError, LabelInvalidFormatError, LABEL_SIZE


storage = Storage()
language, encoding = locale.getdefaultlocale()


def delete(label):
    try:
        storage.remove(label)
        print '%s label was deleted.' % label
    except:
        sys.stderr.write('%s is not a valid label.\n' % label)
        sys.exit(1)


def replace(label, path):
    try:
        storage.replace(label, path)
        print '%s label now points to %s.' % (label, path)
    except LabelTooLongError:
        sys.stderr.write('%s is too long. The size limit is %d characters.\n'
                                                        % (label, LABEL_SIZE))
    except LabelInvalidFormatError:
        sys.stderr.write('%s is not a valid label.\n' % label)

    sys.exit(1)


def add(label, path):
    try:
        storage.add(label, path)
        print '%s label points to %s.' % (label, path)
    except LabelAlreadyExistsError:
        sys.stderr.write('%s label already exists. Use --replace.\n' % label)
        sys.exit(1)
    except LabelTooLongError:
        sys.stderr.write('%s is too long. The size limit is %d characters.\n'
                                                        % (label, LABEL_SIZE))
    except LabelInvalidFormatError:
        sys.stderr.write('%s is not a valid label.\n' % label)

    sys.exit(1)


def main():
    """Entrypoint for the `label` utility."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.set_defaults(mode='insert')
    group.add_argument('-d', '--delete', action='store_const', dest='mode',
                            const='delete', help='delete an existing label')
    group.add_argument('-r', '--replace', action='store_const', dest='mode',
                            const='replace', help='replace an existing label')
    group.add_argument('-i', '--insert', action='store_const', dest='mode',
                                    const='insert', help='insert a new label')
    parser.add_argument('label', nargs='?', help='name of the label')
    parser.add_argument('path', nargs='?', help='path to the directory')
    args = parser.parse_args()

    if not args.label and args.mode in ['delete', 'replace']:
        parser.error('can\'t %s without specify a label.' % args.mode)

    if args.path:
        path = unicode(args.path, encoding)
    else:
        path = unicode(os.getcwd(), encoding)

    if args.label:
        label = unicode(args.label, encoding)
    else:
        label = None

    storage.open_or_create()

    if args.mode == 'delete':
        delete(label)

    elif args.mode == 'replace':
        replace(label, path)

    else:
        if not label:
            label = re.sub(r'\s+', '_', path[path.rfind('/')+1:], flags=re.UNICODE)

        add(label, path)
