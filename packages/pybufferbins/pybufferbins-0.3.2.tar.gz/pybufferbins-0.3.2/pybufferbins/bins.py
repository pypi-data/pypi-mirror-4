from threading import Lock, RLock
from struct import pack, unpack
from glob import glob
from os import makedirs, listdir
from os.path import basename, getsize, exists
from shutil import rmtree

from logging import getLogger
logging = getLogger(__name__)

# Bins are named as record-types, under a directory named for the 
# grouping field's value (program ID, etc.., while the bins are named 
# SdProgram, SdProgramGenre, ...): "<key>/<record type>"
SORT_BYKEY = 'SortByKey'

# Bins are named for the values of the grouping field, and the directory is 
# named for the record-type: "<record type>/<key>". This is the opposite order 
# of SortByKey. This is specifically more useful when you're only pushing one 
# record-type into an index (it will sort a series of records into files based 
# on the grouping-field's value, under a single directory).
SORT_BYTYPE = 'SortByType'


class Bins(object):
    """This class invokes the router, but makes decisions on how to organize
    the bins. It also provides the accessor to read the information by however
    it was grouped.
    """

    def __init__(self, name, root_path, sort_type, context_path=None, 
                 remove_existing=False):
        
        if context_path is None:
            self.__root_path = root_path
        else:
            self.__root_path = ("%s/%s" % (root_path, context_path))

        if remove_existing and exists(root_path):
            rmtree(self.__root_path)

        self.__name = name
        self.__sort_type = sort_type
        self.__handlers = {}
        self.__router = _Router(self.__main_indexer)
        self.__checked_paths = {}

    def __str__(self):
        return ("Bins(NAME=[%s] SORT-TYPE=[%s])" % (self.__name, self.__sort_type))

    @staticmethod
    def foreach_contexts(root_path):
        for context in listdir(root_path):
            yield context

    @staticmethod
    def get_contexts(root_path):
        return sorted(listdir(root_path))

    def add_handler(self, pb_cls, key_attr):

        try:
            type_name = pb_cls.__name__
            if self.__sort_type == SORT_BYKEY:
                info = (pb_cls, self.__idx_group_by_key, key_attr)
            elif self.__sort_type == SORT_BYTYPE:
                info = (pb_cls, self.__idx_group_by_type, key_attr)
            else:
                raise Exception("Type-name [%s] sort-type [%s] is not valid." %
                                (type_name, self.__sort_type))

            self.__handlers[type_name] = info
        except:
            logging.exception("Could not register handler.")
            raise

    def __check_path(self, path):

        if path not in self.__checked_paths:
            if not exists(path):
                makedirs(path)

            self.__checked_paths[path] = True

    def __idx_group_by_key(self, type_name, record, key):

        path = ("%s/%s" % (self.__root_path, key))
        self.__check_path(path)

        file_path = ("%s/%s" % (path, type_name))

        return file_path

    def __idx_group_by_type(self, type_name, record, key):

        path = ("%s/%s" % (self.__root_path, type_name))
        self.__check_path(path)

        file_path = ("%s/%s" % (path, key))

        return file_path

    def __main_indexer(self, type_name, record):

        try:
            (_, callback, key_attr) = self.__handlers[type_name]
        except:
            logging.exception("Can not index unregistered type [%s]." %
                              (type_name))
            raise

        # We were given a key function.
        if hasattr(key_attr, '__call__'):
            key = key_attr(record)
        # We were given an attribute name.
        else:
            key = getattr(record, key_attr)

        try:
            return callback(type_name, record, key)
        except:
            logging.exception("Indexer failed for type-name [%s] and key "
                              "[%s]." % (type_name, key))
            raise

    def get_grouped_data(self, *args, **kwargs):
        if self.__sort_type == SORT_BYKEY:
            return self.__get_grouped_data_bykey(*args, **kwargs)
        elif self.__sort_type == SORT_BYTYPE:
            return self.__get_grouped_data_bytype(*args, **kwargs)
        else:
            raise Exception("Sort-type [%s] is not valid for get-data." % 
                            (self.__sort_type))

    def __get_grouped_data_bykey(self, sorted_key, type_name='*'):
        """If sort-by was BYKEY, return all of the data for all of the types
        stored for the given key.
        """

        search_path = ("%s/%s" % (self.__root_path, sorted_key))

        if not exists(search_path):
            raise LookupError("Search-path [%s] is not valid for token [%s] "
                              "(BY-KEY)." % (search_path, sorted_key))

        if self.__sort_type != SORT_BYKEY:
            raise Exception("Sort-type must be BY-KEY for "
                            "get_grouped_data_bykey.  ACTUAL= [%s]" % 
                            (self.__sort_type))

        found = glob("%s/%s" % (search_path, type_name))

        collected = {}
        for file_path in found:
            type_name = basename(file_path)
            pb_cls = self.__handlers[type_name][0]

            items = []
            for item in Bins.bin_foreach(pb_cls, file_path):
                items.append(item)

            collected[type_name] = items

        return collected

    def __get_grouped_data_bytype(self, sorted_type_name, key='*'):
        """If sort-by was BYTYPE, return all of the data for all of the keys 
        stored for the given type.
        """

        search_path = ("%s/%s" % (self.__root_path, sorted_type_name))

        if not exists(search_path):
            raise LookupError("Search-path [%s] is not valid for type-name "
                              "[%s] (BY-TYPE)." % (search_path, 
                                                   sorted_type_name))

        if self.__sort_type != SORT_BYTYPE:
            raise Exception("Sort-type must be BY-TYPE for "
                            "get_grouped_data_bykey.  ACTUAL= [%s]" % 
                            (self.__sort_type))

        search_pattern = ("%s/%s" % (search_path, key))
        
        found = glob(search_pattern)

        type_name = sorted_type_name
        pb_cls = self.__handlers[type_name][0]

        collected = {}
        for file_path in found:
            items = []
            for item in Bins.bin_foreach(pb_cls, file_path):
                items.append(item)

            collected[basename(file_path)] = items

        return collected

    @staticmethod
    def bin_foreach(pb_cls, file_path):
        """Iterate through entries in a bin file."""

        len_width = 2

        i = 0
        length = getsize(file_path)
        with file(file_path, 'rb') as f:
            while i < length:
                packed_len = f.read(len_width)
                (actual_len,) = unpack('H', packed_len)

                data = f.read(actual_len)

                new = pb_cls()
                new.ParseFromString(data)

                yield new

                i += len_width + len(data)

    def push(self, record):
        """Push a record into one or more bins."""

        self.__router.push(record)

    def flush(self):
        """Clean-up open buffers."""

        self.__router.flush()

    @property
    def name(self):
        return self.__name

    @property
    def root_path(self):
        return self.__root_path

class _Router(object):
    """Class responsible for knowing how to send data to bins."""

    max_handles = 50

    def __init__(self, indexer):
        self.__indexer = indexer

        self.__handles = {}
        self.__locker = RLock()

    def flush(self):
        with self.__locker:
            for type_name, handle in list(self.__handles.items()):
                self.__handles[type_name].close()
                del self.__handles[type_name]

    def push(self, record):
        """Push a record into storage. The indexer will determiner what files
        ("indexes") to append the record to
        """

        with self.__locker:
            type_name = record.__class__.__name__

            try:
                indexes = self.__indexer(type_name, record)
            except:
                logging.exception("Indexing failed for type-name [%s] and "
                                  "record [%s]." % (type_name, record))
                raise

            if indexes.__class__ != list:
                indexes = [indexes]

            for index_filepath in indexes:
                if index_filepath not in self.__handles:
                    if len(self.__handles) >= _Router.max_handles:
#                        logging.debug("Forcing flush of (%d) handles." % (len(self.__handles)))
                        self.flush()

                    handle = file(index_filepath, 'ab')
                    self.__handles[index_filepath] = handle
                else:
                    handle = self.__handles[index_filepath]

                data = record.SerializeToString()
                handle.write(pack('H', len(data)))
                handle.write(data)

        return len(indexes)
