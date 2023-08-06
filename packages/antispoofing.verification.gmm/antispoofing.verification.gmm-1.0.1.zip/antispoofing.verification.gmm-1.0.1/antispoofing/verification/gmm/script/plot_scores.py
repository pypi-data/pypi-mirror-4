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
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks; test set)')
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

  from matplotlib.backends.backend_pdf import PdfPages

  outdir = os.path.dirname(args.output)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)

  pp = PdfPages(args.output)

  # Plot 1: DET
  # -----------

  fig = mpl.figure()
  bob.measure.plot.det(base_neg, base_pos, 100, color='blue', 
      label="Baseline")
  bob.measure.plot.det(over_neg, over_pos, 100, color='black',
      label=args.protocol)
  bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
  mpl.title("DET: %s" % args.title)
  mpl.xlabel("False Rejection Rate (%)")
  mpl.ylabel("False Acceptance Rate (%)")
  mpl.legend()
  mpl.grid()
  pp.savefig()

  # Plot 2.1: Score histograms
  # --------------------------

  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  
  mpl.hist(base_neg, bins=10, color='red', alpha=0.5, label="Impostors",
      normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5, label="True Clients",
      normed=True)

  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.legend()

  mpl.title("Scores: %s" % args.title)
  mpl.grid()
  pp.savefig()

  # Plot 2.2: Score histograms + Threshold
  # --------------------------------------

  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  
  mpl.hist(base_neg, bins=10, color='red', alpha=0.5,
      label="Impostors @ test", normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5, label="True Clients @ test",
      normed=True)

  axlim = mpl.axis()

  hter_thres_baseline = bob.measure.minHterThreshold(base_neg_dev, base_pos_dev)

  # plot the line
  mpl.axvline(x=hter_thres_baseline, ymin=axlim[2], ymax=axlim[3], linewidth=2,
      color='green', linestyle='--', label="Min. HTER @ dev")
  
  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.legend()

  mpl.title("Scores: %s" % args.title)
  mpl.grid()
  pp.savefig()

  # Plot 2.3: Score histograms + Attack Scores
  # ------------------------------------------

  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  
  mpl.hist(base_neg, bins=10, color='red', alpha=0.5,
      label="Impostors @ test", normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5,
      label="True Clients @ test", normed=True)
  mpl.hist(over_neg, bins=20, color='black', alpha=0.5,
      label="%s @ test" % (args.protocol,), normed=True)

  axlim = mpl.axis()

  hter_thres_baseline = bob.measure.minHterThreshold(base_neg_dev, base_pos_dev)

  # plot the line
  mpl.axvline(x=hter_thres_baseline, ymin=axlim[2], ymax=axlim[3], linewidth=2,
      color='green', linestyle='--', label="Min. HTER @ dev")
  
  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.legend()

  # Reports what is the canonical value for a particular attack
  
  mhter_thres_baseline = bob.measure.minHterThreshold(base_neg_dev, base_pos_dev)
  hter_pass_rate = pass_rate(hter_thres_baseline, over_neg)
  print "Attack Success Rate on Min.HTER: %.2f%%" % (100.*hter_pass_rate)

  mpl.title("Scores: %s" % args.title)
  mpl.grid()
  pp.savefig()

  # Plot 2.4: Add Line of Probability of Success
  # --------------------------------------------

  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  
  mpl.hist(base_neg, bins=10, color='red', alpha=0.5,
      label="Impostors @ test", normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5,
      label="True Clients @ test", normed=True)
  mpl.hist(over_neg, bins=20, color='black', alpha=0.5,
      label="%s @ test" % (args.protocol,), normed=True)

  axlim = mpl.axis()

  hter_thres_baseline = bob.measure.minHterThreshold(base_neg_dev, base_pos_dev)

  # plot the line
  mpl.axvline(x=hter_thres_baseline, ymin=axlim[2], ymax=axlim[3], linewidth=2,
      color='green', linestyle='--', label="Min. HTER @ dev")
  
  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.legend()

  # Reports what is the canonical value for a particular attack
  
  hter_pass_rate = pass_rate(hter_thres_baseline, over_neg)

  # scan the range of scores, put an axis on the right with spoofing success
  # probabilities that depend on the threshold
  ntick = 100
  step = (axlim[1] - axlim[0])/float(ntick)
  thres = [(k*step)+axlim[0] for k in range(ntick)]
  mix_prob_y = []
  for k in thres: mix_prob_y.append(100.*pass_rate(k, over_neg))

  prob_ax = ax1.twinx() 
  mpl.plot(thres, mix_prob_y, color='green', label="Success Prob.")
  prob_ax.set_ylabel("Attack Success Probability - ASP (%)", color='green')
  for tl in prob_ax.get_yticklabels(): tl.set_color('green')

  # Inprint the min.HTER one on the plot:
  prob_ax.plot(hter_thres_baseline, 100.*hter_pass_rate, 'o', color='green')
  prob_ax.text(hter_thres_baseline-(hter_thres_baseline-axlim[0])/4.,
      95.*hter_pass_rate, '%.1f%%' % (100.*hter_pass_rate,),
      color='green')

  mpl.title("Scores: %s" % args.title)
  mpl.grid()
  pp.savefig()

  # Plot 3: EPC + adjusted Attack Success Probability
  # -------------------------------------------------

  epc_baseline = epc(base_neg_dev, base_pos_dev, base_neg, base_pos, 100)
  
  fig = mpl.figure()
  ax1 = mpl.subplot(111)
  mpl.plot(epc_baseline[:,0], [100.*k for k in epc_baseline[:,1]],
      color='blue', label='Baseline')

  mpl.xlabel("Weight")
  ax1.set_ylabel("Weighted Error Rate for Baseline Verification (%)", 
      color="blue")
  for tl in ax1.get_yticklabels(): tl.set_color('blue')

  mix_prob_y = []
  for k in epc_baseline[:,2]:
    prob_attack = sum(1 for i in over_neg if i >= k)/float(over_neg.size)
    mix_prob_y.append(100.*prob_attack)

  axlim = mpl.axis()

  prob_ax = ax1.twinx() 
  mpl.plot(epc_baseline[:,0], mix_prob_y, color='green', label="Success Prob.")
  prob_ax.set_ylabel("ASP @ Weighted ER for Different Operating Points (%)",
      color='green')
  for tl in prob_ax.get_yticklabels(): tl.set_color('green')

  mpl.title("EPC: %s" % args.title)
  mpl.grid()
  pp.savefig()

  pp.close() # close multi-page PDF writer

if __name__ == '__main__':
  main()
