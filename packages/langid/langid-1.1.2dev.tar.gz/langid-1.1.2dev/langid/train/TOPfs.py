"""
Select the most highly-weighted N features across any number of files.

Marco Lui, February 2013
"""

import argparse

from common import read_weights, write_features

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-n","--number", type=int, default=200, metavar='N', 
    help="keep top N features per file")
  parser.add_argument("output", metavar='PATH', help="output to PATH")
  parser.add_argument("files", metavar="FILE", nargs='*', help="read weighted features from FILE")
  args = parser.parse_args()

  out_f = open(args.output, 'w') if args.output else sys.stdout
  feats = set()

  for path in args.files:
    w = read_weights(path)
    feats |= set(sorted(w, key=w.get, reverse=True)[:args.number])

  write_features(sorted(feats), args.output)
