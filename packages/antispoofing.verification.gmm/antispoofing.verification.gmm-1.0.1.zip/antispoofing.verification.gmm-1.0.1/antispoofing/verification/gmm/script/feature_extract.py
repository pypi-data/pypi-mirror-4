#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon 31 Oct 15:06:31 2011 

"""Calculates the features for all videos in the replay attack database. We
calculate features for every N frames (configurable) in the video input.
"""

import sys
import os

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('inputdir', metavar='DIR', type=str, help='Root directory containing the raw unprocessed data from the Replay-Attack database')
  
  parser.add_argument('outputdir', metavar='DIR', type=str, help='Directory where the results for the feature extraction will be placed at')
  
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str, dest='config', default=None, help='Filename of the configuration file with parameters for feature extraction and verification (defaults to loading what is in the module "antispoofing.verification.gmm.config.gmm_replay")')

  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exists')

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

  # Imports feature calculation
  from ... import features
  from ... import faceloc

  # Directories containing the images and the annotations
  import bob
  db = bob.db.replay.Database()
  files = db.files(cls=('real', 'attack', 'enroll'),
      directory=args.inputdir, extension='.mov')

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    ordered_keys = sorted(files.keys())
    if pos >= len(ordered_keys):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(ordered_keys))
    key = ordered_keys[pos] # gets the right key
    files = {key: files[key]}

  for index, key in enumerate(sorted(files.keys())):

    stem = db.paths([key])[0]
    sys.stdout.write("Processing file '%s' (%d/%d)" % (stem, index+1, len(files)))
    sys.stdout.flush()
    
    # bootstraps video reader for client
    video = bob.io.VideoReader(files[key])

    # loads face locations - roll localization
    flocfile = os.path.join(args.inputdir, 'face-locations', stem) + '.face'
    locations = faceloc.read_face(flocfile)
    locations = faceloc.expand_detections(locations, video.number_of_frames)

    for frame_index, frame in enumerate(video):

      if (frame_index+1) % config.every_n_frames: 
        sys.stdout.write('_')
        sys.stdout.flush()
        continue

      outputdir = os.path.join(args.outputdir, '%03d' % (frame_index+1))
      output_filename = os.path.join(outputdir, stem) + '.hdf5'

      if frame_index >= len(locations) or not locations[frame_index] or \
          not locations[frame_index].is_valid():
        sys.stdout.write('x')
        sys.stdout.flush()
        continue

      # if we continue, there was a detected face for the present frame
      anthropo = faceloc.Anthropometry19x19(locations[frame_index])

      from ...utils import ensure_dir
      ensure_dir(os.path.dirname(output_filename))

      # some house-keeping commands
      if os.path.exists(output_filename) and not args.force:
        raise RuntimeError, "Output file path %s already exists and you did not --force" % output_filename

      # finally, computes the features for this particular frame
      features.dct.compute_loaded_replay(frame, 
          anthropo.eye_centers(), 
          output_filename,
          config.CROP_EYES_D, 
          config.CROP_H,
          config.CROP_W,
          config.CROP_OH,
          config.CROP_OW, 
          config.GAMMA, 
          config.SIGMA0,
          config.SIGMA1,
          config.SIZE,
          config.THRESHOLD, 
          config.ALPHA, 
          config.BLOCK_H,
          config.BLOCK_W, 
          config.OVERLAP_H,
          config.OVERLAP_W,
          config.N_DCT_COEF)

      sys.stdout.write('.')
      sys.stdout.flush()

    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
  main()
