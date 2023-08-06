# coding: utf-8
import os
import re
import codecs
from configparser import UnicodeConfigParser, NoOptionError


HOME_DIRECTORY = os.path.expanduser("~")
LABEL_STORAGE_FILE = '.goto'
LABEL_STORAGE_PATH = os.path.join(HOME_DIRECTORY, LABEL_STORAGE_FILE)
LABELS_SECTION = u'labels'

LABEL_SIZE = 32

LABEL_RE = re.compile(r'^[^\s/]+$', re.UNICODE)


class Storage(object):
    def __init__(self, file_name=LABEL_STORAGE_PATH, labels_section=LABELS_SECTION):
        self.parser = UnicodeConfigParser()
        self.file_name = file_name
        self.labels_section = labels_section


    ########## FILE MANIPULATION ##########

    def _persist(self):
        """Refreshs the file with the last changes."""
        with codecs.open(self.file_name, 'w', encoding='utf-8') as f:
            self.parser.write(f)


    def _create(self):
        """
        Creates the label file and put a default session where the labels will
        be stored.
        """
        self.parser.add_section(self.labels_section)
        self._persist()


    def open(self):
        """Loads the parser with data from the label file."""
        with codecs.open(self.file_name, 'r', encoding='utf-8') as f:
            self.parser.readfp(f)


    def open_or_create(self):
        """
        Tries to open the label file, if an error occurs, create the file.
        """
        try:
            self.open()
        except IOError:
            self._create()
            self.open()


    ########## LABEL MANIPULATION ##########

    def get(self, label):
        """Returns the path of a label."""
        return self.parser.get(self.labels_section, label)


    def get_all(self):
        """Returns a dictionary with all labels and paths."""
        return {
            label:path for label, path
                in self.parser.items(self.labels_section)
        }


    def replace(self, label, path):
        """
        Replaces the path from a label. The label is created if it not exists.
        """
        if len(label) > LABEL_SIZE:
            raise LabelTooLongError()

        if not LABEL_RE.match(label):
            raise LabelInvalidFormatError()

        self.parser.set(self.labels_section, label, path)
        self._persist()


    def add(self, label, path):
        """
        Adds a label-path entry in the label file. If the label exists, an
        Exception is raised.
        """
        if self.parser.has_option(self.labels_section, label):
            raise LabelAlreadyExistsError()

        self.replace(label, path)


    def remove(self, label):
        """Removes a label and it's path."""
        self.parser.remove_option(self.labels_section, label)
        self._persist()


class LabelAlreadyExistsError(Exception):
    pass

class LabelTooLongError(Exception):
    pass

class LabelInvalidFormatError(Exception):
    pass
