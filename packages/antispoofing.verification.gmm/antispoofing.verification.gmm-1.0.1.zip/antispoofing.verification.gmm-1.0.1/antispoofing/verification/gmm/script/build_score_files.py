#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 07 Nov 2011 17:55:05 CET 

"""Generates face-verification-like performance tables that can be fed to
performance computation scripts. Two tables are always generated: development
and test.
"""

import os
import re
import sys
import bob

CLIENT_RE = re.compile(r'client(?P<n>\d{3})')

def is_attack(filename):
  return filename.find('attack') != -1

def extract_client_no(filename):
  """Extracts the client number from a file"""
  return int(CLIENT_RE.search(os.path.basename(filename)).group(0).replace('client',''))

def write_file(clients, stems, scoredir, frames, thorough, filename, fivecol):
  """Writes a 4 or 5-column file with the data from the stems given"""

  outfile = open(filename, 'w')

  for client_id in clients:

    client_no = extract_client_no(client_id) #this will work!
    score_dir = os.path.join(scoredir, client_id)
    dirs = [k for k in os.listdir(score_dir) if int(k) <= frames]

    for key, stem in stems.iteritems(): #all samples
      data = []

      claimed_id = extract_client_no(stem)

      if is_attack(stem) and claimed_id != client_no:
        #skip attacks to different identities.
        continue

      if not thorough and claimed_id != client_no:
        #skip real-accesses to different identities.
        continue

      if is_attack(stem): claimed_id = 'attack'

      for d in dirs:
        fname = os.path.join(scoredir, client_id, d, stem + '.hdf5')
        if not os.path.exists(fname):
          print "WARNING: Ignoring unexisting file %s" % (fname)
          continue
        data.append(bob.io.load(fname)[0,0])
      if len(data) == 0: 
        average = 0.0
      else:
        average = sum(data)/len(data) #average score for this match
      if fivecol:
        outfile.write('%s %s %s %s %.5e\n' % (client_no, client_no, claimed_id, stem, average))
      else:
        outfile.write('%s %s %s %.5e\n' % (client_no, claimed_id, stem, average))

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('scores', metavar='DIR', type=str, help='Root directory containing the scores per video for the Replay-Attack database')
 
  parser.add_argument('outputdir', metavar='DIR', type=str, help='Directory where the merged scores will be saved at')
  
  parser.add_argument('-p', '--protocol', metavar='PROTOCOL', type=str,
      dest='protocol', help='The name of the protocol to use when evaluating the performance of the data on face verification (defaults to "%(default)s)". If you do *not* specify a protocol, just run the baseline face verification.')

  parser.add_argument('-t', '--thorough', default=False,
      dest='thorough', action='store_true', help='If set will be thorough for client/impostor scores concerning real-accesses (not attacks) while comparing the client model')

  parser.add_argument('-f', '--frames', metavar='INT', type=int,
      dest='frames', default=10, help='Number of frames to average the scores from')

  parser.add_argument('-5', '--5col', action='store_true', dest='fivecol',
      default=False, help='Writes a 5-column file format (instead of the default 4 column format)')

  parser.add_argument('-c', '--config-file', metavar='FILE', type=str, dest='config', default=None, help='Filename of the configuration file with parameters for feature extraction and verification (defaults to loading what is in the module "antispoofing.verification.gmm.config.gmm_replay")')

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

  # An adjustment
  if not args.protocol and not args.thorough:
    print "warning: Forcing 'thorough' on baseline..."
    args.thorough = True

  # Database
  db = bob.db.replay.Database()

  # Finds the files that belong to the negative and positive samples of each
  # of the experiment groups: devel, test
  print "Querying database for model names...",
  sys.stdout.flush()
  client_dict = db.files(cls='enroll', groups=('devel'))
  dev_client = set()
  for key, value in client_dict.iteritems():
    client_id = value.split('_')[0].split('/')[2]
    dev_client.add(client_id)
  dev_client = sorted(list(dev_client))
  client_dict = db.files(cls='enroll', groups=('test'))
  test_client = set()
  for key, value in client_dict.iteritems():
    client_id = value.split('_')[0].split('/')[2]
    test_client.add(client_id)
  test_client = sorted(list(test_client))
  print "%d development;" % len(dev_client),
  print "%d test" % len(test_client)

  # Finds all files for real access
  print "Querying database for real/devel files...",
  sys.stdout.flush()
  if not args.protocol:
    dev_real_dict = db.files(cls='real', groups=('devel'))
  else:
    dev_real_dict = db.files(cls=('real', 'attack'), groups=('devel'),
        protocol=args.protocol)
  print "%d files" % (len(dev_real_dict))

  print "Querying database for real/test files...",
  sys.stdout.flush()
  if not args.protocol:
    test_real_dict = db.files(cls='real', groups=('test'))
  else:
    test_real_dict = db.files(cls=('real', 'attack'), groups=('test'),
        protocol=args.protocol)
  print "%d files" % (len(test_real_dict))

  # Setup a name template:
  template = '%s'
  proto = args.protocol if args.protocol is not None else 'baseline'
  template += ('-%s' % proto)
  if args.thorough: template += '-thorough'
  template += ('-%d' % args.frames)
  if args.fivecol: template += '.5c'
  else: template += '.4c'

  args.outputdir = os.path.join(args.outputdir)

  if not os.path.exists(args.outputdir): os.makedirs(args.outputdir)

  # Runs the whole shebang for writing an output file
  devfile = os.path.join(args.outputdir, template % 'devel')
  write_file(dev_client, dev_real_dict, args.scores, args.frames,
      args.thorough, devfile, args.fivecol)
  print "wrote: %s" % devfile

  testfile = os.path.join(args.outputdir, template % 'test')
  write_file(test_client, test_real_dict, args.scores, args.frames,
      args.thorough, testfile, args.fivecol)
  print "wrote: %s" % testfile

if __name__ == '__main__':
  main()
