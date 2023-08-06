#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 13 Jul 2012 10:41:32 CEST

"""Calculates UBM statistics for all input videos in the Replay Attack database"""

import os
import sys

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('features', metavar='DIR', type=str, help='Root directory containing the extracted features from the Replay-Attack database')
  
  parser.add_argument('ubm', metavar='FILE', type=str, help='The trained UBM')
  
  parser.add_argument('outputdir', metavar='DIR', type=str, help='Directory where the results for the statistics generation will be placed at')
  
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config', help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')

  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exist')

  # For SGE grid processing @ Idiap
  parser.add_argument('--grid', dest='grid', action='store_true', default=False, help=argparse.SUPPRESS)

  from ..version import __version__
  name = os.path.basename(os.path.splitext(sys.argv[0])[0])
  parser.add_argument('-V', '--version', action='version',
      version='PB-GMM for ReplayAttack Database v%s (%s)' % (__version__, name))
  
  args = parser.parse_args()

  # Loads the configuration 
  if args.config is None:
    import antispoofing.verification.gmm.config.gmm_replay as config
  else:
    import imp
    config = imp.load_source('config', args.config)

  # Database
  import bob
  db = bob.db.replay.Database()

  # Run for attacks and real-accesses for the development and test groups
  process = db.files(cls=('attack','real'), groups=('devel', 'test'))

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    ordered_keys = sorted(process.keys())
    if pos >= len(ordered_keys):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(ordered_keys))
    key = ordered_keys[pos] # gets the right key
    process = {key: process[key]}

  # Directories containing the features
  features_input = []
  gmmstats_output = []
  for d in os.listdir(args.features):
    for key, value in process.iteritems():
      features_input.append(os.path.join(args.features, d, value + '.hdf5'))
      gmmstats_output.append(os.path.join(args.outputdir, d, value + '.hdf5'))

  # Loads the UBM
  if not os.path.exists(args.ubm):
    RuntimeError, "Cannot load UBM from file '%s'" % (args.ubm)
  ubm = bob.machine.GMMMachine(bob.io.HDF5File(args.ubm))

  from .. import generate_statistics

  generate_statistics(dict(enumerate(features_input)), ubm,
      dict(enumerate(gmmstats_output)), args.force)

if __name__ == "__main__": 
  main()
