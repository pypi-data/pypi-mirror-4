#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
from .. import utils
import numpy
import bob

def load_data(files):
  """Concatenates a list of arrays into an arrayset"""
  data = bob.io.load(files)
  return data

def normalize_std_arrayset(arrayset):
  """Applies a unit variance normalization to an arrayset"""

  # Initializes variables
  n_samples = arrayset.shape[0]
  length = arrayset.shape[1]
  mean = numpy.ndarray((length,), 'float64')
  std = numpy.ndarray((length,), 'float64')

  mean.fill(0)
  std.fill(0)

  # Computes mean and variance
  for k in range(n_samples):
    x = arrayset[k,:].astype('float64')
    mean += x
    std += (x ** 2)

  mean /= n_samples
  std /= n_samples
  std -= (mean ** 2)
  std = std ** 0.5 # sqrt(std)

  ar_std_list = []
  for k in range(n_samples):
    ar_std_list.append(arrayset[k,:].astype('float64') / std)
  ar_std = numpy.vstack(ar_std_list)

  return (ar_std,std)


def multiplyVectorsByFactors(matrix, vector):
  """Used to unnormalise some data"""
  for i in range(0, matrix.shape[0]):
    for j in range(0, matrix.shape[1]):
      matrix[i, j] *= vector[j]


def train_ubm(train_files, ubm_filename, n_gaussians=512, iterk=500,
    iterg=500, convergence_threshold=0.0005, variance_threshold=0.0005,
    update_weights=True, update_means=True, update_variances=True,
    norm_KMeans=False):
  """Trains a Universal Background Model and saves it to file"""

  # Loads the data into an arrayset
  ar = load_data(train_files.itervalues())

  # Computes input size
  input_size = ar.shape[1]

  # Normalizes the arrayset if required
  if not norm_KMeans:
    normalizedAr = ar
  else:
    (normalizedAr,stdAr) = normalize_std_arrayset(ar)

  # Creates the machines (KMeans and GMM)
  kmeans = bob.machine.KMeansMachine(n_gaussians, input_size)
  gmm = bob.machine.GMMMachine(n_gaussians, input_size)

  # Creates the KMeansTrainer
  kmeansTrainer = bob.trainer.KMeansTrainer()
  kmeansTrainer.convergence_threshold = convergence_threshold
  kmeansTrainer.max_iterations = iterk

  # Trains using the KMeansTrainer
  kmeansTrainer.train(kmeans, normalizedAr)

  [variances, weights] = kmeans.get_variances_and_weights_for_each_cluster(normalizedAr)
  means = kmeans.means

  # Undoes the normalization
  if norm_KMeans:
    multiplyVectorsByFactors(means, stdAr)
    multiplyVectorsByFactors(variances, stdAr ** 2)

  # Initializes the GMM
  gmm.means = means
  gmm.variances = variances
  gmm.weights = weights
  gmm.set_variance_thresholds(variance_threshold)

  # Trains the GMM
  trainer = bob.trainer.ML_GMMTrainer(update_means, update_variances, update_weights)
  trainer.convergence_threshold = convergence_threshold
  trainer.max_iterations = iterg
  trainer.train(gmm, ar)

  # Saves the UBM to file
  gmm.save(bob.io.HDF5File(ubm_filename, 'w'))

def generate_statistics(features_input, ubm, gmmstats_output, force=False):
  """Computes GMM statistics against a UBM"""

  # Initializes GMMStats object 
  gmmstats = bob.machine.GMMStats(ubm.dim_c, ubm.dim_d)

  # Processes the 'dictionary of files'
  for k in features_input:

    # Removes old file if required
    if force == True and os.path.exists(gmmstats_output[k]):
      print "Remove old statistics %s." % (gmmstats_output[k])
      os.remove(gmmstats_output[k])

    if not os.path.exists(features_input[k]):
      print "Ignoring non-existing file %s..." % features_input[k]
      continue

    if os.path.exists(gmmstats_output[k]):
      print "GMM statistics %s already exists."  % (gmmstats_output[k])

    else:
      print "Computing statistics from features %s." % (features_input[k])
      # Loads input features file
      features = bob.io.load(str(features_input[k]))

      # Accumulates statistics
      gmmstats.init()

      try:
       ubm.acc_statistics(features, gmmstats)

      except Exception, e:
        print "Exception caught treating file %s => %s" % (features_input[k],e)
        continue

      # Saves the statistics
      utils.ensure_dir(os.path.dirname( str(gmmstats_output[k]) ))
      gmmstats.save(bob.io.HDF5File( str(gmmstats_output[k]), 'w' ))

def enrol(enrol_files, model_path, ubm_filename, iterg=1,
    convergence_threshold=0.0005, variance_threshold=0.0005,
    relevance_factor=4, responsibilities_threshold=0, adapt_weight=False,
    adapt_variance=False, torch3_map=False, alpha_torch3=0.5):
  """Enrols a GMM using MAP adaptation"""

  # Loads the data into an arrayset
  ar = load_data(enrol_files.itervalues())

  # Loads the UBM/prior gmm
  if not os.path.exists(ubm_filename):
      raise RuntimeError, "Cannot find UBM %s" % (ubm_filename)
  ubm = bob.machine.GMMMachine(bob.io.HDF5File(ubm_filename))    
  ubm.set_variance_thresholds(variance_threshold)

  # Creates the trainer
  if responsibilities_threshold == 0.:
    trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, adapt_variance, adapt_weight)
  else:
    trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, adapt_variance, adapt_weight, responsibilities_threshold)
  trainer.convergenceThreshold = convergence_threshold
  trainer.max_iterations = iterg
  trainer.set_prior_gmm(ubm)

  if torch3_map:
    trainer.set_t3_map(alpha_torch3)

  # Creates a GMM from the UBM
  gmm = bob.machine.GMMMachine(ubm)
  gmm.set_variance_thresholds(variance_threshold)

  # Trains the GMM
  trainer.train(gmm, ar)

  # Saves it to the given file
  gmm.save(bob.io.HDF5File(model_path, 'w'))

def score(model_filename, probe_file, probe_output, ubm_filename):
  """Computes a split of the A matrix for the ZT-Norm and saves the raw scores to file"""
  
  # Loads the UBM 
  if not os.path.exists(ubm_filename):
      raise RuntimeError, "Cannot find UBM %s" % (ubm_filename)
  ubm = bob.machine.GMMMachine(bob.io.HDF5File(ubm_filename))

  # Loads the models
  model = []
  if not os.path.exists(model_filename):
    raise RuntimeError, "Could not find model %s." % model_filename
  model = [bob.machine.GMMMachine(bob.io.HDF5File(model_filename))]

  # For every probe, run an individual test
  for k,v in enumerate(probe_file):
    stats = [bob.machine.GMMStats(bob.io.HDF5File(str(v)))]
    # Saves the A row vector for each model and Z-Norm samples split
    A = bob.machine.linear_scoring(model, ubm, stats, [], True)
    utils.ensure_dir(os.path.dirname(probe_output[k]))
    bob.io.save(A, probe_output[k])
    print "Processed (%d/%d)\n  %s\n  %s" % (k+1, len(probe_file), v, probe_output[k])
