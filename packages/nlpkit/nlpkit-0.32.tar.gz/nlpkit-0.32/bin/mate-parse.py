#!/usr/bin/env python
import argparse
import codecs
import logging
import os
from nlpkit.parse.mate import parse, MateParser

parser = argparse.ArgumentParser(description="Lemmatizes, tags and parses raw text with the mate-tools parser")
parser.add_argument('in_file', help="Raw text with one document per line. Assumed to be in UTF-8")
parser.add_argument('--out_file', '-o', help='Processed text in CONLL9 format', required=True)
parser.add_argument('--map_file', '-m', help='Mapping between sentences and documents', required=True)
parser.add_argument('--mate-dir', help='Path to the mate parser')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if not args.mate_dir:
    for dir in os.environ['PATH'].split(os.pathsep):
        jar_locations = [os.path.join(dir, 'anna-3.3.jar'), os.path.join(os.path.join(dir, 'mate'), 'anna-3.3.jar')]
        found_files = [jar_location for jar_location in jar_locations if os.path.isfile(jar_location)]
        if len(found_files) > 0:
            mate_dir = os.path.dirname(found_files[0])
            break
    if not mate_dir:
        raise "Mate parser not found in PATH (searching for anna-3.3.jar and mate/anna-3.3.jar)"
else:
    mate_dir = args.mate_dir



docs =  (line.strip() for line in codecs.open(args.in_file, encoding='utf-8', errors='ignore'))
parse(docs, args.out_file, args.map_file, parser=MateParser(mate_dir=mate_dir))
