"""
Utility functions for reading and writing files in the svmrank format,
which augments the svmlight sparse matrix format by adding a 'qid' (query id)
element for each row with the effect of grouping multiple rows together.

Scikit-learn has a nice and well-tested implementation of readers and writers for
the svmlight format (without qid). The interface here is inspired by the scikit-learn
code, but doesn't directly borrow from it. Simply wrapping the existing functions--
for the writer adding the qid element as a postprocessing step, and for the reader
removing  it in preprocessing--would be an alternative, perhaps preferable way
of implemening this functionality.
"""
import codecs

from scipy.sparse import lil_matrix
import numpy as np
import sys

def dump_svmrank_file(X, y, qids, fname):
    with open(fname, 'w') as out:
        for row, label, qid in zip(X, y, qids):
            sorted_keys = sorted(row.nonzero()[1])
            feat_str = " ".join(["{}:{}".format(k,row[0,k])
                                 for k in sorted_keys
                                 if row[0,k] != 0])
            print >>out, "{target} qid:{qid} {features}".format(target=label, qid=qid, features=feat_str)

def load_svmrank_files(files, n_features=None):
    r = [_parse_svmrank_file(fname) for fname in files]
    if n_features is None:
        n_features = 0
        for rows in r:
            for target, qid, kv_pairs in rows:
                max_k = kv_pairs[-1][0]
                if max_k >= n_features:
                    n_features = max_k + 1
    
    res = []
    for rows in r:
#        print "Allocating matrix of shape {}".format((len(rows), n_features))
        X = lil_matrix((len(rows), n_features))
        y = np.zeros(len(rows))
        qids = np.zeros(len(rows))
        for i, (target, qid, kv_pairs) in enumerate(rows):
            for k,v in kv_pairs:
                X[i,k] = v
            y[i] = target
            qids[i] = qid
        res += [X.tocsr(), y, qids]
    return res

def load_svmrank_file_with_map(fname, feature_names, feature_map):
    rows = _parse_svmrank_file(fname)
    X = lil_matrix((len(rows), len(feature_map)))
    y = np.zeros(len(rows))
    qids = np.zeros(len(rows))
    for i, (target, qid, kv_pairs) in enumerate(rows):
        for col_i,v in kv_pairs:
            name = feature_names[col_i]
            X[i,feature_map[name]] = v
        y[i] = target
        qids[i] = qid
    return X.tocsr(), y, qids


def load_feature_name_file(fname, max_len=None):
    if fname:
        names = map(unicode.strip, codecs.open(fname, encoding='utf-8').readlines())
    elif max_len:
        names = ["f{}".format(i) for i in range(max_len)]
    else:
        raise "Either a file name or the maximum number of features must be given"

    return np.array(names)




def _parse_svmrank_file(fname):
    with open(fname) as file:
        res = []
        for line in file:
            comment_begin = line.find("#")
            if comment_begin != -1: line = line[:comment_begin]
            line = line.strip()
            parts = line.split(" ")
            target = int(parts[0])
            qid = parts[1].split(":")[1]
            kv_pairs = [feature.split(":") for feature in parts[2:]]
            kv_pairs = [(int(k), np.float(v)) for k,v in kv_pairs]
            res.append((target, qid, kv_pairs))
        return res

class AddQidFile(object):
    def __init__(self, file, qids):
        self.file = file
        self.qids = qids
        self._linebuf = None

    def write(self, str):
        lines = str.split("\n")
        # The first and the last line of the input may be partial.
        # The first line is complete if 'lines' contains more than one element.
        # Checking whether the last line is complete can be done by seeing the
        # the last character of the input is a newline character



        # Last line from previous call was not complete
        if self._linebuf:
            self._linebuf += lines[0]
            if len(lines) > 1: # First line is complete
                self._write_line(self._linebuf)
                self._linebuf = None
            lines = lines[1:]


        # Last line in this call is incomplete
        if lines[-1] != '':
            self._linebuf = lines[-1]
            # Take the last line out, whether incomplete or blank
        lines = lines[:-1]


        for line in lines: self._write_line(line)

    def _write_line(self, line):
        if not line.startswith("#"):
            first_space_index = line.find(" ")
            line = "{} {} {}".format(line[:first_space_index], "QID", line[first_space_index+1:])
        self.file.write(line)


if __name__ == '__main__':
    f=AddQidFile(sys.stdout, [1,2,3])
    f.write("# Hello darkness\n")
    f.write("1 1:1 2:1 3:0 ")
    f.write("1:1 2:1 3:0 ")
    f.write("# okay \n")
    f.write("-1 1:2 2:2 3:3 \n")




#        while str:
#            nl_index = str.find('\n')
#            self._linebuf += str[:]
#
#        self.file.write()

