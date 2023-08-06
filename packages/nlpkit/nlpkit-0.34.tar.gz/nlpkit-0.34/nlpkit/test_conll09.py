from unittest import TestCase
import unittest
from nlpkit.conll09 import sentence_to_table, sentences_by_document

CONLL09_FILE = """1	Essential	_	essential	_	JJ	_	_	-1	2	_	NMOD	_	_
2	oils	_	oil	_	NNS	_	_	-1	4	_	SBJ	_	_
3	certainly	_	certainly	_	RB	_	_	-1	4	_	ADV	_	_
4	were	_	be	_	VBD	_	_	-1	0	_	ROOT	_	_
5	available	_	available	_	JJ	_	_	-1	4	_	PRD	_	_
6	in	_	in	_	IN	_	_	-1	4	_	LOC	_	_
7	Biblical	_	biblical	_	NNP	_	_	-1	8	_	NAME	_	_
8	Times	_	times	_	NNP	_	_	-1	6	_	PMOD	_	_
9	.	_	.	_	.	_	_	-1	4	_	P	_	_

1	I	_	i	_	PRP	_	_	-1	2	_	SBJ	_	_
2	think	_	think	_	VBP	_	_	-1	0	_	ROOT	_	_
3	it	_	it	_	PRP	_	_	-1	4	_	SBJ	_	_
4	's	_	's	_	VBZ	_	_	-1	2	_	OBJ	_	_
5	a	_	a	_	DT	_	_	-1	7	_	NMOD	_	_
6	great	_	great	_	JJ	_	_	-1	7	_	NMOD	_	_
7	book	_	book	_	NN	_	_	-1	4	_	OBJ	_	_
8	.	_	.	_	.	_	_	-1	2	_	P	_	_
"""

CONLL09_SENT = CONLL09_FILE.split("\n\n")[0]

class TestConll09(TestCase):
    def test_sentence_to_table(self):
        table = sentence_to_table(CONLL09_SENT.split("\n"))
        columns = set(['id', 'form', 'lemma', 'plemma', 'pos', 'ppos', 'feat', 'pfeat', 'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'pred'])
        self.assertEquals(set(table.keys()), columns)
        for k in table.keys():
            self.assertEqual(len(table[k]), 9)
        self.assertEquals(table['form'][0], 'Essential')

    def test_sentences_by_document(self):
        one_doc_map = iter(["0", "0"])
        two_docs_map = iter(["0", "1"])

        one_doc = list(sentences_by_document(CONLL09_FILE, one_doc_map))
        self.assertEqual(len(one_doc), 1)

        two_docs = list(sentences_by_document(CONLL09_FILE, two_docs_map))
        self.assertEqual(len(two_docs), 2)




if __name__ == '__main__':
    unittest.main()