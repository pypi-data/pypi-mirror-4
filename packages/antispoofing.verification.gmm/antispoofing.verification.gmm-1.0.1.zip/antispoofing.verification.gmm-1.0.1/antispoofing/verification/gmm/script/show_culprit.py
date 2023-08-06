#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 08 Nov 2011 09:52:57 CET 

"""Show misclassifications in 4-column score files, for true claim matches.
"""

import os
import sys

def main():

  if len(sys.argv) != 3:
    print __doc__
    print "usage: %s filename threshold"
    sys.exit(1)

  T = float(sys.argv[2])

  f = open(sys.argv[1], 'rt')
  data = [k.split() for k in f.readlines()]
  values = v = [[int(k[0]), int(k[1]), k[2], float(k[3])] for k in data]
  for i, d in enumerate(values):
    if d[0] == d[1] and d[3] < T:
      print "%s: %.5e" % (d[2], d[3])

if __name__ == '__main__':
  main()
