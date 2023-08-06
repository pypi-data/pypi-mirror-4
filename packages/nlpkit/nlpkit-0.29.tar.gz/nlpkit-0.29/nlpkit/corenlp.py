from collections import namedtuple
from functools import partial, wraps
import codecs
from glob import glob
from itertools import chain, groupby
import logging
import shutil
from lxml import etree
from tempfile import mkdtemp, mktemp
from subprocess import check_output

import networkx as nx

def _sentiter(func):
    return lambda self: [func(self, sent) for sent in self._sents()]

def sents_iter(f):
    @wraps(f)
    def wrapper(self):
        return [f(self, sent) for sent in self._sents()]
    return wrapper

CoreNLPMention = namedtuple("CoreNLPMention", "representative, sentence, start, end, head")

class CoreNLPDoc(object):
    def __init__(self, xml_str):
        self._xml_str = xml_str

    def getdoc(self):
        if not hasattr(self, '_doc'):
            self._doc = etree.fromstring(self._xml_str)
        return self._doc

    doc = property(getdoc)

    def _sents(self):
        return self.doc.xpath("//sentences/sentence")

    @sents_iter
    def cparses(self, sent):
        parse_elem = sent.find("parse")
        if parse_elem is not None:
            return parse_elem.text.strip()

    @sents_iter
    def tokens(self, sent):
        return [dict((elem.tag, elem.text) for elem in token.getchildren())
                for token in sent.findall("tokens/token")]

    def _dparse(self, sent, dep_type=None):
        G = nx.DiGraph()
#        G.add_node(0, word='ROOT')

        for i, token in enumerate(sent.findall("tokens/token")):
            G.add_node(i+1, word=token.findtext("word"), pos=token.findtext("POS"))

        for dep in sent.findall(dep_type + "/dep"):
            gov_idx = int(dep.find("governor").get("idx"))
            dep_idx = int(dep.find("dependent").get("idx"))
            G.add_edge(gov_idx, dep_idx, deprel=dep.get('type'))

#        for n in G.nodes():
#            if n != 0 and G.in_degree(n) == 0:
#                G.add_edge(0, n, deprel='root')

        return G

    def corefs(self):
        mentions_list = []
        for coref in self.doc.findall(".//coreference/coreference"):
            mentions = set()
            for mention_elem in coref.findall("mention"):
                mention = CoreNLPMention(representative=mention_elem.get("representative") == "true",
                    sentence=int(mention_elem.findtext("sentence"))-1,
                    start=int(mention_elem.findtext("start"))-1,
                    end=int(mention_elem.findtext("end"))-1,
                    head=int(mention_elem.findtext("head"))-1,

                )
                mentions.add(mention)
            mentions_list.append(mentions)
        return mentions_list

    @sents_iter
    def triplets(self, sent):
        sent_len = len(sent.findall("tokens/token"))
        tups = [(None, 'root')]*sent_len

        dep_type = "basic-dependencies"
        deps = sent.findall(dep_type + "/dep")
        if deps:
            for dep in deps:
                gov_idx = int(dep.find("governor").get("idx"))
                dep_idx = int(dep.find("dependent").get("idx"))
                tups[dep_idx-1] = (gov_idx-1, dep.get('type'))
            return tups
        else:
            return None

    @sents_iter
    def basic_deps(self, sent):
        return self._dparse(sent, dep_type='basic-dependencies')

    @sents_iter
    def collapsed_deps(self, sent):
        return self._dparse(sent, dep_type='collapsed-dependencies')

    @sents_iter
    def collapsed_cc_deps(self, sent):
        return self._dparse(sent, dep_type='collapsed-ccprocessed-dependencies')

class CoreNLPField(object):
    def __init__(self, field):
        self.field = field

    def sents(self, key='word'):
        sentences = self.field.get(key, [])
        return [[tok.replace(u'\u237D', u' ') for tok in sent.split(u" ")]
                for sent in sentences]

    def flat(self, key='word'):
        return list(chain(*self.sents(key)))

    def ner(self, key='word', flat=True):
        def extract(ners, tokens):
            ner_groups = []
            for s, g in groupby(enumerate(ners), lambda x: x[1]):
                if s == 'O': continue
                group = list(g)
                ner_groups.append((s, u' '.join(tokens[group[0][0]:group[-1][0]+1])))
            return ner_groups

        if flat:
            return extract(self.flat('ner'), self.flat(key))
        else:
            return [extract(ners, tokens)
                    for ners, tokens in zip(self.sents('ner'), self.sents(key))]


def parse_texts(texts, jar_dir, prop_file=None, keep_files=False):
    temp_dir = mkdtemp("corenlp")
    logging.debug("Creating temporary dir for input texts: {}".format(temp_dir))
    fnames = [mktemp(dir=temp_dir) for text in texts]
    filelist_file = mktemp(dir=temp_dir)
    with open(filelist_file, 'w') as f:
        f.writelines("\n".join(fnames))

    try:
        logging.debug("Writing raw texts to files")
        for fname, text in zip(fnames, texts):
            with codecs.open(fname, 'w', encoding='utf-8') as file:
                file.write(text)

        opts = ['java',
              '-cp', ':'.join(glob(jar_dir + "/*.jar")),
              '-Xmx3g',
              'edu.stanford.nlp.pipeline.StanfordCoreNLP'
              ]

        if prop_file:
            opts += ['-props', prop_file]
        opts += ['-filelist', filelist_file]
        opts += ['-outputDirectory', temp_dir]

        logging.debug("Executing: {}".format(" ".join(opts)))
        out = check_output(opts)

        parsed_fnames = [fname + '.xml' for fname in fnames]
        # As of corenlp 1.3.1 there are sometimes encoding issues with the generated XML file
        cleaned_files = [codecs.open(fname, encoding='utf-8', errors='replace').read()
                         for fname in parsed_fnames]

        return [CoreNLPDoc(c_file.encode('utf-8')) for c_file in cleaned_files]

    finally:
        if not keep_files:
            logging.debug("Cleaning up in temporary dir: {}".format(temp_dir))
            shutil.rmtree(temp_dir)
        else:
            logging.info("Not cleaning temporary dir: {}".format(temp_dir))