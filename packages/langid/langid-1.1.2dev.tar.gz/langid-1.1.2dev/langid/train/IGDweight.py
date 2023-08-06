"""
pairlangfeats.py
Compute features for a language pair

Marco Lui, February 2013
"""

import argparse, os, csv
import numpy

from langid.train.common import read_weights, write_weights

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-o","--output", metavar="PATH", help = "write weights to PATH")
  parser.add_argument("--no_norm", default=False, action="store_true", help="do not normalize difference in p(t|C) by sum p(t|C)")
  parser.add_argument("lang1", metavar='LANG', help="first language")
  parser.add_argument("lang2", metavar='LANG', help="second language")
  parser.add_argument('model', metavar="MODEL_DIR", help="path to langid.py training model dir (used for lang_index and DF_all)")
  args = parser.parse_args()

  model_dir = args.model

  def m_path(name):
    return os.path.join(model_dir, name)

  # Where to do output
  if args.output:
    weights_path = args.output
  else:
    if args.no_norm:
      weights_path = m_path('IGDfeats.no_norm.{0}.{1}'.format(args.lang1, args.lang2))
    else:
      weights_path = m_path('IGDfeats.{0}.{1}'.format(args.lang1, args.lang2))

  print "reading lang_index"
  with open(m_path("lang_index")) as f:
    reader = csv.reader(f)
    langs = zip(*reader)[0]

  print "reading langbin"
  lb_w = read_weights(m_path('IGweights.lang.bin'))
  index1 = langs.index(args.lang1)
  index2 = langs.index(args.lang2)

  w = {}
  for f in lb_w:
    w_l1 = lb_w[f][index1]
    w_l2 = lb_w[f][index2]
    if args.no_norm:
      w[f] = abs(w_l1 - w_l2)
    else:
      w[f] = abs(w_l1 - w_l2) / (w_l1 + w_l2)

  write_weights(w, weights_path)
  print "wrote weights to {0}".format(weights_path)
