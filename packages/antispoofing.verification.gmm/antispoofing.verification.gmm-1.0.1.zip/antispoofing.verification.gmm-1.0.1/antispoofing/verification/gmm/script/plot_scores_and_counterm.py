#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 10 Nov 2011 08:33:57 CET 

"""Plot scores for different groups of data.
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob
import numpy as np
import argparse

def epc(dev_negatives, dev_positives, test_negatives, test_positives, points):
  """Reproduces the bob.measure.epc() functionality, but returns the
  thresholds on the 3rd column of the input data."""

  retval = np.ndarray((points, 3), 'float64')
  step = 1./(float(points)-1.)

  for i in range(points):
    retval[i,0] = i*step
    retval[i,2] = bob.measure.minWeightedErrorRateThreshold(dev_negatives,
        dev_positives, retval[i,0])
    retval[i,1] = sum(bob.measure.farfrr(test_negatives, test_positives, retval[i,2]))/2.

  return retval

def pass_rate(threshold, attacks):
  """Calculates the rate of attacks that are after a certain threshold"""

  return sum(1 for i in attacks if i >= threshold)/float(attacks.size)

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('baseline_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification (development set)')
  parser.add_argument('baseline_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification (test set)')
  parser.add_argument('overlay_dev', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks; development set)')
  parser.add_argument('overlay_test', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks + cm; test set)')
  parser.add_argument('baseline_dev_cm', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification + cm (development set)')
  parser.add_argument('baseline_test_cm', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification + cm (test set)')
  parser.add_argument('overlay_dev_cm', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks + cm; development set)')
  parser.add_argument('overlay_test_cm', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks + cm; test set)')
  parser.add_argument('-p', '--overlay-protocol', metavar='STR', type=str,
      dest='protocol', default="", help='Legend that will be used for the overlaied negatives (spoofing attacks)')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-o', '--output', metavar='FILE', type=str,
      default='plots.pdf', dest='output',
      help='Set the name of the output file (defaults to "%(default)s")')

  args = parser.parse_args()

  if not args.title: 
    args.title = os.path.splitext(os.path.basename(args.overlay_test))[0]
  if not args.protocol: 
    args.protocol = os.path.splitext(os.path.basename(args.overlay_test))[0]

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline_test)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay_test)
  [base_neg_dev, base_pos_dev] = bob.measure.load.split_four_column(args.baseline_dev)
  [over_neg_dev, over_pos_dev] = bob.measure.load.split_four_column(args.overlay_dev)

  [base_neg_cm, base_pos_cm] = bob.measure.load.split_four_column(args.baseline_test_cm)
  [over_neg_cm, over_pos_cm] = bob.measure.load.split_four_column(args.overlay_test_cm)
  [base_neg_dev_cm, base_pos_dev_cm] = bob.measure.load.split_four_column(args.baseline_dev_cm)
  [over_neg_dev_cm, over_pos_dev_cm] = bob.measure.load.split_four_column(args.overlay_dev_cm)

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  # Plot 1: DET
  # -----------

  fig = mpl.figure()
  bob.measure.plot.det(base_neg, base_pos, 1000, color='blue', linestyle='dashed', alpha=0.8, label="Baseline - CM")
  bob.measure.plot.det(over_neg, over_pos, 1000, color='black', linestyle='dashed', alpha=0.8, label="%s - CM" % (args.protocol,))
  bob.measure.plot.det(base_neg_cm, base_pos_cm, 1000, color='blue', label="Baseline + CM")
  bob.measure.plot.det(over_neg_cm, over_pos_cm, 1000, color='black', label="%s + CM" % (args.protocol,))
  bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
  mpl.title("DET: %s" % args.title)
  mpl.xlabel("False Rejection Rate (%)")
  mpl.ylabel("False Acceptance Rate (%)")
  mpl.legend()
  mpl.grid()
  pp.savefig()

  # Plot 2: EPC + adjusted Attack Success Probability
  # -------------------------------------------------

  epc_baseline = epc(base_neg_dev, base_pos_dev, base_neg, base_pos, 100)
  epc_baseline_cm = epc(base_neg_dev_cm, base_pos_dev_cm, 
      base_neg_cm, base_pos_cm, 100)
  
  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  mpl.plot(epc_baseline[:,0], [100.*k for k in epc_baseline[:,1]],
      color='blue', alpha=0.8, linestyle='dashed', label='Baseline - CM')
  mpl.plot(epc_baseline_cm[:,0], [100.*k for k in epc_baseline_cm[:,1]],
      color='blue', label='Baseline + CM')

  mpl.xlabel("Weight")
  ax1.set_ylabel("Weighted Error Rate for Baseline Verification (%)", 
      color="blue")
  for tl in ax1.get_yticklabels(): tl.set_color('blue')

  mix_prob_y = []
  mix_prob_y_cm = []
  for k in epc_baseline[:,2]:
    prob_attack = sum(1 for i in over_neg if i >= k)/float(over_neg.size)
    prob_attack_cm = sum(1 for i in over_neg_cm if i >= k)/float(over_neg_cm.size)
    mix_prob_y.append(100.*prob_attack)
    mix_prob_y_cm.append(100.*prob_attack_cm)

  axlim = mpl.axis()

  prob_ax = ax1.twinx() 
  mpl.plot(epc_baseline[:,0], mix_prob_y, color='green', alpha=0.8, linestyle='dashed', label="Success Prob. - CM")
  mpl.plot(epc_baseline_cm[:,0], mix_prob_y_cm, color='green', label="Success Prob. + CM")
  prob_ax.set_ylabel("ASP @ Weighted ER for Different Operating Points (%)",
      color='green')
  for tl in prob_ax.get_yticklabels(): tl.set_color('green')

  mpl.title("EPC: %s" % args.title)
  mpl.grid()
  pp.savefig()

  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
