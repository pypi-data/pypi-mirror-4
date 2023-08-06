#from nltk import sent_tokenize, word_tokenize
import logging
import os
import re
import subprocess
from tempfile import NamedTemporaryFile
import nltk

def prepare_documents(docs, token_file, map_file,
                      sent_tokenize=nltk.sent_tokenize, word_tokenize=nltk.word_tokenize,
                      max_sentence_len=75):
    """Splits each document into sentences and further into tokens.
        Writes a file with document to sentence mappings"""
    for doc_i, doc in enumerate(docs):
        # Squeeze repetitions of characters from the set '?!.', keeping the last one
        re.sub(r"(([!\?.]\s?)\s*)+", r"\2", doc)
        for sent_i, sent in enumerate(sent_tokenize(doc)):
            tokens = word_tokenize(sent)
            if len(tokens) == 0:
                continue
            if max_sentence_len and len(tokens) > max_sentence_len:
                tokens = tokens[:max_sentence_len]

            if not (doc_i == 0 and sent_i == 0):
                map_file.write("\n")
                token_file.write("\n")
            map_file.write("{}".format(doc_i))

            for tok_i, tok in enumerate(tokens, 1):
                row = [unicode(tok_i), tok] + [u"_"]*13
                row_as_text = u"\t".join(row) + u"\n"
                token_file.write(row_as_text.encode('utf-8'))


class MateParser(object):
    def __init__(self, mate_dir, lemma_model='eng-lemma-3.model', tag_model='tag-eng-3.model',
                 parse_model='english-parser-graph-based-v3.model'):
        self.mate_dir = mate_dir
        self.lemma_model = os.path.join(self.mate_dir, lemma_model)
        self.tag_model = os.path.join(self.mate_dir, tag_model)
        self.parse_model = os.path.join(self.mate_dir, parse_model)
        self.class_path = "{}/anna-3.3.jar".format(self.mate_dir)

    def tag(self, in_filename, out_filename):
        """Takes as input a CONLL9 formatted file and augments it with lemmas and tags"""
        # Lemmatizer
        lemma_file = NamedTemporaryFile()
        self._run_cmd(['java', '-Xmx2G', '-cp', self.class_path,
                       'is2.lemmatizer.Lemmatizer',  '-model', self.lemma_model,
                       '-test', in_filename,
                       '-out', lemma_file.name])

        # Tagger
        self._run_cmd(['java', '-Xmx2G', '-cp', self.class_path,
                       'is2.tag.Tagger',  '-model', self.tag_model,
                       '-test', lemma_file.name,
                       '-out', out_filename])

        lemma_file.close()

    def parse(self, in_filename, out_filename):
        """Takes as input a CONLL9 formatted file and augments it with lemmas, tags, and parses"""
        # Lemmatizer
        tag_file = NamedTemporaryFile()
        self.tag(in_filename, tag_file.name)

        # Parser
        self._run_cmd(['java', '-Xmx6G', '-cp', self.class_path,
                       'is2.parser.Parser',  '-model', self.parse_model,
                       '-test', tag_file.name,
                       '-out', out_filename])

        tag_file.close()

    def _run_cmd(self, args):
        logging.info("Running command as: {}".format(u' '.join(args)))
        subprocess.call(args)


def parse(docs, out_filename, map_filename, parser, only_tag=False, max_sentence_len=75):
    map_file = open(map_filename, 'w')
    token_file = NamedTemporaryFile()
    prepare_documents(docs, token_file, map_file, max_sentence_len=max_sentence_len)
    token_file.flush()
    if only_tag:
        parser.tag(token_file.name, out_filename)
    else:
        parser.parse(token_file.name, out_filename)