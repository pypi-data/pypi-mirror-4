#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 13 Jul 2012 14:00:47 CEST

"""Enrolls GMMs for the Replay-Attack database using MAP adaptation"""

import os
import sys

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('features', metavar='DIR', type=str, help='Root directory containing the extracted features from the Replay-Attack database')
 
  parser.add_argument('ubm', metavar='FILE', type=str, help='The trained UBM')
  
  parser.add_argument('outputdir', metavar='DIR', type=str, help='Directory where the models will be saved at')
  
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str, dest='config', default=None, help='Filename of the configuration file with parameters for feature extraction and verification (defaults to loading what is in the module "antispoofing.verification.gmm.config.gmm_replay")')

  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exists')
  
  parser.add_argument('--grid', dest='grid', action='store_true',
      default=False, help=argparse.SUPPRESS)

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

  # Enrollment files
  process = db.files(cls="enroll", groups=("devel", "test"))

  # Temporary hack to get model ids - note: there is no client data that can be
  # in both sets (development and test), so it is ok to cluster all data in a
  # client-based dictionary.
  enroll_files = {}
  for key, value in process.iteritems():
    client = value.split('_')[0].split(os.sep)[2] #terrible hack!
    for d in os.listdir(args.features):
      f = os.path.join(args.features, d, value + '.hdf5')
      if enroll_files.has_key(client): enroll_files[client].append(f)
      else: enroll_files[client] = [f]

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(enroll_files):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(enroll_files))
    only_id = sorted(enroll_files.keys())[pos]
    enroll_files = {only_id: enroll_files[only_id]}

  # Checks that the base directory for storing the models exists
  from ...utils import ensure_dir
  ensure_dir(args.outputdir)

  # Trains the models
  from .. import enrol

  for model_id in sorted(enroll_files.keys()):

    # Path to the model
    model_path = os.path.join(args.outputdir, str(model_id) + ".hdf5")

    # Removes old file if required
    if args.force and os.path.exists(model_path):
      print "Removing old GMM model"
      os.remove(model_path)

    if os.path.exists(model_path):
      print "Model %s already exists." % model_path
    else:
      print "Enrolling model %s..." % model_path
      enrol(dict(enumerate(enroll_files[model_id])),
          model_path, 
          args.ubm,
          config.iterg_enrol,
          config.convergence_threshold,
          config.variance_threshold,
          config.relevance_factor,
          config.responsibilities_threshold)

if __name__ == "__main__": 
  main()
