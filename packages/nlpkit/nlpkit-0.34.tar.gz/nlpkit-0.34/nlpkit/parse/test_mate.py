import os
from tempfile import NamedTemporaryFile
from unittest import TestCase
import unittest
from mate import prepare_documents, MateParser
import StringIO

__author__ = 'anders'
docs = ['To be sure. It was just so.',
        'Arthur sighed with delight. An amber folding chair!']

class TestMate(TestCase):
    def test_prepare_for_tagging(self):
        tag_file = StringIO.StringIO()
        map_file = StringIO.StringIO()

        prepare_documents(docs, tag_file, map_file)
        tag_file_contents = tag_file.getvalue()
        map_file_contents = map_file.getvalue()

        self.assertEqual(len(tag_file_contents.split("\n")), 23)
        self.assertEqual(map_file_contents.split("\n"), ['0', '0', '1', '1'])

    def test_mate_parser(self):
        in_file = NamedTemporaryFile('w', delete=False)
        out_file = NamedTemporaryFile('r')
        prepare_documents(docs, in_file, StringIO.StringIO())
        in_file.close()

        mate = MateParser(mate_dir='/users/anders/bin/mate') # Default settings
        mate.parse(in_file.name, out_file.name)

        os.remove(in_file.name)

        print out_file.read()




if __name__ == '__main__':
    unittest.main()
