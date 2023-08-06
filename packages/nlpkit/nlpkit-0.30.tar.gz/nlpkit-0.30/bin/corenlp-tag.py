#!/usr/bin/env python
from collections import defaultdict
import argparse
import codecs
import json

from bson import json_util

from nlpkit.corenlp import parse_texts

parser = argparse.ArgumentParser(description="""Given a stream of JSON documents,
enrich with structured information from Stanford CoreNLP, and generate update documents""")
parser.add_argument('mongo_file', help='File with a list of JSON documents - one on each line')
parser.add_argument('output_file', help='File receiving the JSON output documents')
parser.add_argument('--prefix', help='Add prefix to field', default='corenlp_')
parser.add_argument('--jar-dir', '--jar', help="Path to CoreNLP jar files",
    default='/Users/anders/bin/stanford-corenlp-2012-05-22')
parser.add_argument('--prop-file', '--prop', help="CoreNLP property file")
#parser.add_argument('--update', action='store_true', help='Generate a document using update modifiers')
parser.add_argument('--fields', nargs='*', help="Process only the listed fields")
parser.add_argument('--cache', action='store_true', help='Cache results from parser')
parser.add_argument('--no-clean', action='store_true', dest='keep_files', default=False)
args = parser.parse_args()

in_file = codecs.open(args.mongo_file, encoding='utf-8')
out_file = codecs.open(args.output_file, 'w', encoding='utf-8')

docs = [json.loads(l, object_hook=json_util.object_hook) for l in in_file]
reconsile = [(i, key, val) for i, doc in enumerate(docs)
                           for key, val in doc.items()
                           if key != '_id'
                           if not args.fields or key in args.fields]
vals = [tup[2] for tup in reconsile]

if not args.prop_file:
    args.prop_file = args.jar_dir + "/StanfordCoreNLP.properties"

if args.cache:
    from joblib import Memory
    mem = Memory(cachedir='/tmp/joblib')
    parse_texts = mem.cache(parse_texts)

parsed_vals = parse_texts(vals, jar_dir=args.jar_dir, prop_file=args.prop_file, keep_files=args.keep_files)
for parsed_val, (i, key, _) in zip(parsed_vals, reconsile):
    out_doc = {'_id': docs[i]['_id']}
    cparse = parsed_val.cparses()

    parses = {
        'basic_dep': parsed_val.basic_deps(),
        'collapsed_dep': parsed_val.collapsed_deps(),
        'collapsed_cc_dep': parsed_val.collapsed_cc_deps()
    }

    tokens = parsed_val.tokens()

    def tokenstr(sent_toks, field):
        return u' '.join([unicode(tok[field]).replace(u' ', u'\u237D')
                for tok in sent_toks])

    def depstr(G):
        edgestrs = [u'{}({},{})'.format(data['deprel'], u, v) for u,v,data in G.edges(data=True)]
        return u' '.join(edgestrs)

    corenlp_field = defaultdict(list)

    for sent_i in range(len(tokens)):
        for parse_name, parse_results in parses.items():
            if len(parse_results) > sent_i:
                corenlp_field[parse_name].append(depstr(parse_results[sent_i]))

        for field in ['lemma', 'word', 'POS', 'NER']:
            corenlp_field[field.lower()].append(tokenstr(tokens[sent_i], field))

        if len(cparse) > sent_i:
            corenlp_field['cparse'].append(cparse[sent_i])

    if not '$set' in out_doc:
        out_doc["$set"] = {}
    out_doc["$set"][args.prefix + key] = corenlp_field

    print >>out_file, json.dumps(out_doc, default=json_util.default)