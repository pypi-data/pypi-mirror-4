# coding: utf-8
from collections import defaultdict
from itertools import izip, count, groupby
from pprint import pprint
from joblib import Parallel, delayed
import nltk
from pymongo import Connection

def in_chunks_of(docs, chunk_size):
    for _, chunk in groupby(izip(count(0), docs), key=lambda t: t[0] / chunk_size):
        yield [t[1] for t in chunk]

class Wrapper(object):
    """The wrapper comes from Cédric Julien who suggested it in a stackoverflow answer:
    http://stackoverflow.com/questions/7089386/pickling-boost-python-functions
    """
    def __init__(self, method_name, module_name):
        self.method_name = method_name
        self.module_name = module_name

    def __call__(self, *args, **kwargs):
        method = __import__(self.module_name, globals(), locals(), [self.method_name,])
        return method(*args, **kwargs)


def nltk_wordpunct_tokenize(sentence):
    return nltk.wordpunct_tokenize(sentence)

def nltk_sent_tokenize(str):
    return nltk.sent_tokenize(str)


def nltk_batch_pos_tag(tokenized_sents):
    return nltk.batch_pos_tag(tokenized_sents)


def tag_doc_chunk(docs, process, serialize):
    # Assemble a long list of sentences extracted from all the given documents.
    # Keep a record of where they came from.  Sentences are identified by a (doc_id, field_name) tuple
    sent_doc_field_map = []
    all_sents = []
    for doc in docs:
        for field, text in doc.items():
            if field == '_id':
                continue
            text = process.preprocess(text)
            doc_sents = [process.word_tokenize(sent) for sent in process.sent_tokenize(text)]
            sent_doc_field_map += [(doc['_id'], field)] * len(doc_sents)
            all_sents += doc_sents

    # Batch process all sentences. This step is the reason why we assemble all sentences
    # into a long list.
    all_tagged_sents = process.batch_pos_tag(all_sents)

    # Create output documents for the processeded sentences
    sents_per_doc_grouper = groupby(zip(sent_doc_field_map, all_tagged_sents), lambda t: t[0][0])
    for doc_id, sents_in_doc in sents_per_doc_grouper:
        new_doc = {}
        # for field_name, sents in groupby(sents_in_doc, lambda composite_id: composite_id[1]):
        #     sents = [s for _,s in sents]
        #     new_doc[field_name] = {
        #         'tok': [[pair[0] for pair in sent] for sent in sents],
        #         process.tag_name: [[pair[1] for pair in sent] for sent in sents],
        #     }

        for composite_id, sent in sents_in_doc:
            _, field = composite_id
            if field not in new_doc:
                new_doc[field] = defaultdict(list)
            new_doc[field]['tok'].append([pair[0] for pair in sent])
            new_doc[field][process.tag_name].append([pair[1] for pair in sent])

        for field in new_doc.keys():
            for name in new_doc[field].keys():
                new_doc[field][name] = u"\n".join([" ".join(sent) for sent in new_doc[field][name]])
            new_doc[field] = dict(new_doc[field])

        new_doc['_id'] = doc_id

        serialize(dict(new_doc))


def tag_docs(cursor, process, serialize=None, n_jobs=-1, chunk_size=1000):
    """Beware: the functions must be of the type function
    """
    par = Parallel(n_jobs=n_jobs, verbose=100)
    par(delayed(tag_doc_chunk)(doc_group, process=process, serialize=serialize)
        for doc_group in in_chunks_of(cursor, chunk_size))


class NltkTagger(object):
    def __init__(self,
                 sent_tokenize=nltk_sent_tokenize,
                 word_tokenize=nltk_wordpunct_tokenize,
                 batch_pos_tag=nltk_batch_pos_tag,
                 preprocess=None):
        self._sent_tokenize = sent_tokenize
        self._word_tokenize = word_tokenize
        self._batch_pos_tag = batch_pos_tag
        self._preprocess = preprocess
        self.tag_name = 'pos'

    def sent_tokenize(self, str):
        return self._sent_tokenize(str)

    def word_tokenize(self, sent):
        return self._word_tokenize(sent)

    def batch_pos_tag(self, tokenized_sents):
        return self._batch_pos_tag(tokenized_sents)

    def preprocess(self, str):
        if self._preprocess:
            return self._preprocess(str)
        else:
            return str

if __name__ == '__main__':
    conn = Connection()
    posts = conn.stackqa.programmers.posts
    ann = posts.annotations

    def save(new_doc):
        # text = "\n".join([" ".join(["/".join(pair) for pair in sent]) for sent in new_doc[]])
        pprint(new_doc)
        ann.save(new_doc)

    docs = posts.find({}, {'Body': 1}).limit(10)
    tag_docs(docs, process=NltkTagger(), serialize=save)