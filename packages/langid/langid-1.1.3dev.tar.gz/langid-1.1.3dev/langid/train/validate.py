"""
Run a langid.py model against its own training data.

Marco Lui, January 2013
"""

from langid.langid import LanguageIdentifier
import csv, sys, os
import argparse
from itertools import izip
from common import MapPool

def setup_pass_langid(model_path):
  global __identifier
  print "setting up an identifier"
  __identifier = LanguageIdentifier.from_modelpath(model_path)

def pass_langid(path):
  global __identifier
  with open(path) as f:
    cl = identifier.classify(f.read())[0]
  return cl


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-j","--jobs", type=int, metavar='N', help="spawn N processes (set to 1 for no paralleization)")
  parser.add_argument("model", metavar='MODEL_DIR', help="read from MODEL_DIR")
  parser.add_argument("output", metavar='OUTPUT_PATH', help="write csv output to OUTPUT_PATH (- for stdout)")

  args = parser.parse_args()

  model_path = os.path.join(args.model, 'model')
  index_path = os.path.join(args.model, 'paths')
  lang_path = os.path.join(args.model, 'lang_index')

  print >>sys.stderr, "model path:", model_path
  print >>sys.stderr, "index path:", index_path
  print >>sys.stderr, "lang path:", lang_path

  # read list of languages in order
  with open(lang_path) as f:
    reader = csv.reader(f)
    langs = zip(*reader)[0]

  # read list of items to classify
  with open(index_path) as f:
    reader = csv.reader(f)
    items = list(reader)

  writer = csv.writer(sys.stdout if args.output == '-' else open(args.output, 'w'))
  
  
  p_langs, paths = zip(*( (langs[int(lang_id)],path) for _, lang_id, path in items))

  with MapPool(args.jobs, setup_pass_langid, (model_path,)) as f:
    pass_langid_out = izip(p_langs, f(pass_langid, paths), paths)

  # write out only rows where GS does not match CL
  writer.writerows((r for r in pass_langid_out if r[0] != r[1]))
