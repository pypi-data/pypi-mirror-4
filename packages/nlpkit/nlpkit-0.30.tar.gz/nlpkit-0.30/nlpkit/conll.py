import unittest
import networkx as nx
import numpy

CONLL_SENTENCE = """1	But	But	CC	CC	but	19	CC	-	-
2	while	while	IN	IN	while	8	VMOD	-	-
3	the	the	DT	DT	the	7	NMOD	-	-
4	New	New	NNP	NNP	new	5	NMOD	-	-
5	York	York	NNP	NNP	08159924-n	7	NMOD	-	-
6	Stock	Stock	NNP	NNP	13333833-n	7	NMOD	-	-
7	Exchange	Exchange	NNP	NNP	11409538-n	8	SBJ	-	-
8	did	did	VBD	VBD	00010435-v	1	COORD	-	-
9	n't	n't	RB	RB	n't	8	ADV	-	-
10	fall	fall	VB	VB	02358655-v	8	VC	-	-
11	apart	apart	RB	RB	apart	10	ADV	-	-
12	Friday	Friday	NNP	NNP	15164463-n	10	ADV	-	-
13	as	as	IN	IN	as	10	ADV	-	-
14	the	the	DT	DT	the	18	NMOD	-	-
15	Dow	Dow	NNP	NNP	dow	16	NMOD	-	-
16	Jones	Jones	NNP	NNP	jone	18	NMOD	-	-
17	Industrial	Industrial	NNP	NNP	industrial	18	NMOD	-	-
18	Average	Average	NNP	NNP	05856979-n	19	SBJ	-	-
19	plunged	plunged	VBD	VBD	00601043-v	0	ROOT	-	-
20	<num>	<num>	CD	CD	190.58	21	NMOD	-	-
21	points	points	NNS	NNS	13830305-n	19	ADV	-	-
22	--	--	:	:	--	23	P	-	-
23	most	most	JJS	JJS	01555732-a	21	OBJ	-	-
24	of	of	IN	IN	of	23	NMOD	-	-
25	it	it	PRP	PRP	it	24	PMOD	-	-
26	in	in	IN	IN	in	23	ADV	-	-
27	the	the	DT	DT	the	29	NMOD	-	-
28	final	final	JJ	JJ	01579128-a	29	NMOD	-	-
29	hour	hour	NN	NN	15228378-n	26	PMOD	-	-
30	--	--	:	:	--	23	P	-	-
31	it	it	PRP	PRP	it	33	SBJ	-	-
32	barely	barely	RB	RB	00073763-r	33	ADV	-	-
33	managed	managed	VBD	VBD	02587532-v	19	ADV	-	-
34	to	to	TO	TO	to	35	VMOD	-	-
35	stay	stay	VB	VB	02619122-v	33	OBJ	-	-
36	this	this	DT	DT	this	37	NMOD	-	-
37	side	side	NN	NN	08649345-n	35	PRD	-	-
38	of	of	IN	IN	of	37	NMOD	-	-
39	chaos	chaos	NN	NN	13976322-n	38	PMOD	-	-
40	.	.	.	.	.	19	P	-	-
"""

CONLL_GOLD_SENTENCE = """1	But	_	CC	_	_	33	CC	_	_
2	while	_	IN	_	_	8	VMOD	_	_
3	the	_	DT	_	_	7	NMOD	_	_
4	New	_	NNP	_	_	5	NMOD	_	_
5	York	_	NNP	_	_	7	NMOD	_	_
6	Stock	_	NNP	_	_	7	NMOD	_	_
7	Exchange	_	NNP	_	_	8	SBJ	_	_
8	did	_	VBD	_	_	33	ADV	_	_
9	n't	_	RB	_	_	8	ADV	_	_
10	fall	_	VB	_	_	8	VC	_	_
11	apart	_	RB	_	_	10	ADV	_	_
12	Friday	_	NNP	_	_	10	ADV	_	_
13	as	_	IN	_	_	19	VMOD	_	_
14	the	_	DT	_	_	18	NMOD	_	_
15	Dow	_	NNP	_	_	16	NMOD	_	_
16	Jones	_	NNP	_	_	18	NMOD	_	_
17	Industrial	_	NNP	_	_	18	NMOD	_	_
18	Average	_	NNP	_	_	19	SBJ	_	_
19	plunged	_	VBD	_	_	10	ADV	_	_
20	190.58	_	CD	_	_	21	NMOD	_	_
21	points	_	NNS	_	_	19	ADV	_	_
22	--	_	:	_	_	23	P	_	_
23	most	_	JJS	_	_	21	PRN	_	_
24	of	_	IN	_	_	23	NMOD	_	_
25	it	_	PRP	_	_	24	PMOD	_	_
26	in	_	IN	_	_	23	ADV	_	_
27	the	_	DT	_	_	29	NMOD	_	_
28	final	_	JJ	_	_	29	NMOD	_	_
29	hour	_	NN	_	_	26	PMOD	_	_
30	--	_	:	_	_	23	P	_	_
31	it	_	PRP	_	_	33	SBJ	_	_
32	barely	_	RB	_	_	33	ADV	_	_
33	managed	_	VBD	_	_	0	ROOT	_	_
34	to	_	TO	_	_	35	VMOD	_	_
35	stay	_	VB	_	_	33	OBJ	_	_
36	this	_	DT	_	_	37	NMOD	_	_
37	side	_	NN	_	_	35	PRD	_	_
38	of	_	IN	_	_	37	NMOD	_	_
39	chaos	_	NN	_	_	38	PMOD	_	_
40	.	_	.	_	_	33	P	_	_"""

def example_sent(text):
    reader = ConllReader(text.split("\n"), Conll2007Format())
    return list(reader.sents())[0]

class Conll2007Format(object):
    def __init__(self):
        self.fields = []
        self.field('id', 'Token counter, starting at 1 for each new sentence.')
        self.field('form', 'Word form or punctuation symbol.')
        self.field('lemma', 'Lemma or stem (depending on particular data set) of word form, or an underscore if not available.')
        self.field('cpostag', 'Coarse-grained part-of-speech tag, where tagset depends on the language.')
        self.field('postag', 'Fine-grained part-of-speech tag, where the tagset depends on the language, or identical to the coarse-grained part-of-speech tag if not available.')
        self.field('feats', 'Unordered set of syntactic and/or morphological features (depending on the particular language), separated by a vertical bar (|), or an underscore if not available.')
        self.field('head', 'Head of the current token, which is either a value of ID or zero (\'0\'). Note that depending on the original treebank annotation, there may be multiple tokens with an ID of zero.')
        self.field('deprel', 'Dependency relation to the HEAD. The set of dependency relations depends on the particular language. Note that depending on the original treebank annotation, the dependency relation may be meaningful or simply \'ROOT\'.')
        self.field('phead', 'Projective head of current token, which is either a value of ID or zero (\'0\'), or an underscore if not available. Note that depending on the original treebank annotation, there may be multiple tokens an with ID of zero. The dependency structure resulting from the PHEAD column is guaranteed to be projective (but is not available for all languages), whereas the structures resulting from the HEAD column will be non-projective for some sentences of some languages (but is always available).')
        self.field('pdeprel', 'Dependency relation to the PHEAD, or an underscore if not available. The set of dependency relations depends on the particular language. Note that depending on the original treebank annotation, the dependency relation may be meaningful or simply \'ROOT\'.')

    def field(self, name, desc):
        self.fields.append(name)

    def format_line(self, attrs):
        fields = [  attrs[field_name] if field_name in attrs else '_'
                    for field_name in self.fields]
        return "\t".join(fields)

    @classmethod
    def from_file(cls, filename):
        return ConllReader(open(filename), cls()).sents()

class ConllReader(object):
    def __init__(self, lineiter, format=Conll2007Format()):
        self._format = format
        self._lineiter = lineiter

    def sents(self):
        for chunk in self._sent_chunks():
            parsed_lines = [dict(zip(self._format.fields, line.split('\t'))) for line in chunk]
            yield Sentence.from_dicts(parsed_lines)

    def _sent_chunks(self):
        lines = []
        for line in self._lineiter:
            if not line.strip(): # Blank line
                yield lines
                lines = []
            else:
                lines.append(line.strip())
        if len(lines) > 0: yield lines

    def write_each_sent(self, func_name, writer):
        for sent in self.sents():
            writer.write([func_name(sent)])

class ConllWriter(object):
    def __init__(self, out_file, format=Conll2007Format()):
        self._format = format
        self._out_file = out_file

    def write(self, sents):
        first_line = True
        sents_iter = iter(sents)
        while True:
            if first_line == False:
                self._out_file.write("\n")
            try:
                sent = sents_iter.next()
                self._out_file.write(self._format_sent(sent))
                first_line = False
            except StopIteration:
                break

    def _format_sent(self, sent):
        lines = [self._format.format_line(sent.G.node[i]) + "\n"
                 for i in range(1, len(sent.G))]
        return "".join(lines)



class Sentence(object):
    def __init__(self):
        self.G = nx.DiGraph()
        self.G.add_node(0)

    def add_node(self, n):
        self.G.add_node(int(n['id']), n)
        self.G.add_edge(int(n['head']), int(n['id']), deprel=n['deprel'])

    def score(self, parsed_sent):
        '''Scores a parsed sentence (given by the parameter) against a sentence with gold relations.
        Returns a tuple of (correct_unlabeled, correct_labeled, total)'''
        unlabeled = set(self.G.in_edges()) & set(parsed_sent.G.in_edges())
        labeled = [(src, target) for src, target in unlabeled
                    if self.G[src][target]['deprel'] == parsed_sent.G[src][target]['deprel']]
        return (len(unlabeled), len(labeled), len(self.G.in_edges()))

    def token_nodes(self):
        return range(1, len(self.G))

    def feats(self, node_id):
        return self.G.node[node_id]['feats']

    def attrs(self, node_id):
        return self.G.node[node_id]


    @classmethod
    def from_dicts(cls, dicts):
        s = Sentence()
        for dict in dicts:
            s.add_node(dict)
        return s

class CorpusScorer(object):
    def __init__(self, sents, gold_sents):
        self._sents = sents
        self._gold_sents = gold_sents
        self.scores = self._scores()
        self._labeled, self._unlabeled, self._total = self.scores.sum(axis=0)

    def uas(self):
        return float(self._unlabeled) / self._total

    def las(self):
        return float(self._labeled) / self._total

    def _scores(self):
        return numpy.array(
                [  gold_sent.score(sent)
                  for sent, gold_sent in zip(self._sents, self._gold_sents)])

class SentenceTest(unittest.TestCase):
    def test_parse_sent(self):
        reader = ConllReader(CONLL_SENTENCE.split("\n"), Conll2007Format())
        sents = list(reader.sents())
        self.assertEqual(len(sents), 1)
        self.assertTrue(isinstance(sents[0], Sentence))
        
    def test_build_graph(self):
        sent = example_sent(CONLL_SENTENCE)
        self.assertEqual(len(sent.G.nodes()), 41)

    def test_score(self):
        sent      = example_sent(CONLL_SENTENCE)
        gold_sent = example_sent(CONLL_GOLD_SENTENCE)
        score = gold_sent.score(sent)
        self.assertEqual(score, (34,33,40))


if __name__ == '__main__':
    unittest.main()
