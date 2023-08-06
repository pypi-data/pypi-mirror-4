#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Jul 2012 09:44:07 CEST

"""Derives the Universal Background Model for the Gaussian-Mixture modelling
using selected frames from the training images in the enrollment subset.
"""

import os
import sys

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('inputdir', metavar='DIR', type=str, help='Root directory containing the extracted features from the Replay-Attack database')
  
  parser.add_argument('output', metavar='FILE', type=str, help='Filepath where to place the trained UBM with the ".hdf5" extension (e.g. "ubm.hdf5")')
  
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str, dest='config', default=None, help='Filename of the configuration file with parameters for feature extraction and verification (defaults to loading what is in the module "antispoofing.verification.gmm.config.gmm_replay")')

  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exists')
  
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

  # Remove old file if required
  if args.force and os.path.exists(args.output):
    os.remove(args.output)

  # Database access
  import bob
  db = bob.db.replay.Database()

  # Checks that the base directory for storing the ubm exists
  from ...utils import ensure_dir
  ensure_dir(os.path.dirname(args.output))

  train_files = []
  for d in os.listdir(args.inputdir):

    inputdir = os.path.join(args.inputdir, d)
    
    if int(d) > config.frames_to_use: 
      print "Skipping directory %s" % inputdir
      continue
    
    print "Considering directory %s" % inputdir

    # grab all files in the train/enrollment subset
    more_files = db.files(directory=inputdir, extension='.hdf5',
        cls=('enroll'), groups=('train'),)
    train_files.extend(more_files.values())

  print "Number of training files: %d" % len(train_files)

  from .. import train_ubm
  ubm = train_ubm(dict(enumerate(train_files)), 
      args.output,
      config.nb_gaussians,
      config.iterk,
      config.iterg_train,
      config.end_acc,
      config.var_thd,
      config.update_weights,
      config.update_means,
      config.update_variances,
      config.norm_KMeans
      )

if __name__ == "__main__": 
  main()
