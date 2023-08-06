from itertools import count
import logging
import sys
import codecs
import json

from bson import json_util

def json_load(filename):
    if filename == "-":
        file = sys.stdin
    else:
        file = codecs.open(filename)
    for lineno, line in enumerate(file, 1):
        try:
            yield json.loads(line, object_hook=json_util.object_hook)
        except Exception as e:
            logging.error("JSON error in line {} of file {}".format(lineno, filename))
            raise e

class JSONDumper(object):
    def __init__(self, filename):
        self._filename = filename
        if filename == '-':
            self._file = sys.stdout
        else:
            self._file = codecs.open(filename, 'w', encoding='utf-8')

    def dump(self, doc):
        print >>self._file, json.dumps(doc, default=json_util.default)

    def close(self):
        if self._filename != '-':
            self._file.close()

def json_dump(iterable, fname):
    dumper = JSONDumper(fname)
    for doc in iterable:
        dumper.dump(doc)
    dumper.close()

def json_map(map_func, fname_in, fname_out):
    dumper = JSONDumper(fname_out)
    for doc in json_load(fname_in):
        dumper.dump(map_func(doc))
    dumper.close()


def values_with_path(items, stack=[]):
    if not items: return []
    k,v = items[0]
    rest = values_with_path(items[1:], stack)
    if isinstance(v, dict):
        return values_with_path(v.items(), stack + [k]) + rest
    elif isinstance(v, list):
        return values_with_path([(i,v) for i,v in enumerate(v)] + items[1:], stack + [k]) + rest
    else:
        path = u".".join(unicode(elem) for elem in stack + [k])
        return [(v,path)] + rest

def mongo_checkout(docs_iter, value_fname, key_fname=None, plain=True):
    if not key_fname:
        key_fname = value_fname + ".reconsile"

    reconsile_dumper = JSONDumper(key_fname)
    if plain:
        value_file = codecs.open(value_fname, 'w', encoding='utf-8')
    else:
        value_dumper = JSONDumper(value_fname)

    for doc in docs_iter:
        for val, path in values_with_path([item for item in doc.items() if item[0] != '_id']):
            reconsile_dumper.dump({'_id': doc['_id'], 'path': path})
            if plain:
                print >>value_file, val
            else:
                value_dumper.dump(val)

def flatten_list(data):
    if isinstance(data, list):
        items = enumerate(data)
    elif isinstance(data, dict):
        items = data.items()
    else:
        return
    for k,v in items:
        if isinstance(v, list) and not any([isinstance(elem, (list, dict)) for elem in v]):
            data[k] = u"\n".join(unicode(elem) for elem in v)
        else:
            flatten_list(v)

def mongo_checkoutfiles(docs_iter, value_dir, key_fname, flatten=True):
    filecounter = count()

    reconsile_dumper = JSONDumper(key_fname)

    for doc in docs_iter:
        if flatten:
            flatten_list(doc)
        for val, path in values_with_path([item for item in doc.items() if item[0] != '_id']):
            fileid = filecounter.next()
            reconsile_dumper.dump({'_id': doc['_id'], 'path': path, 'file': fileid})
            with codecs.open("{}/{}".format(value_dir, fileid), 'w', encoding='utf-8') as file:
                print >>file, val


def mongo_checkin(value_fname, key_fname, collection, plain=True, replace=None, prefix='', suffix=''):
    reconsile_file = codecs.open(key_fname)
    value_file = codecs.open(value_fname)

    print "{} {}".format(value_fname, key_fname)
    for reconsile_line, value_line in zip(reconsile_file, value_file):
        reconsile_doc = json.loads(reconsile_line, object_hook=json_util.object_hook)
        path_elems = reconsile_doc['path'].split(".")
        last_name_idx = [i for i, elem in enumerate(path_elems) if not elem.isdigit()][-1]
        if replace:
            path_elems[last_name_idx] = u''+replace
        path_elems[last_name_idx] = u'' + prefix+ path_elems[last_name_idx] + suffix
        path = u'.'.join(path_elems)

        if plain:
            value = value_line.strip()
        else:
            value = json.loads(value_line, object_hook=json_util.object_hook)

#        print >>sys.stderr, '.',
#        print "Updating collection: ", {'_id': reconsile_doc['_id']}, {'$set': {path: value}}
        collection.update({'_id': reconsile_doc['_id']}, {'$set': {path: value}})


