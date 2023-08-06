#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
import bob
import numpy

def ensure_dir(dirname):
  """ Creates the directory dirname if it does not already exist,
      taking into account concurrent 'creation' on the grid.
      An exception is thrown if a file (rather than a directory) already 
      exists. """
  try:
    # Tries to create the directory
    os.makedirs(dirname)
  except OSError:
    # Check that the directory exists
    if os.path.isdir(dirname): pass
    else: raise

def split_dictionary(input_dict, nb_unit_per_subdict):
  """Splits a dictionary into a list of subdictionaries"""  
  res = []
  sdict = {}
  to_append = False
  for k in sorted(input_dict.keys()):
    sdict[k] = input_dict[k] 
    to_append = True
    # checks if the subdictionary is full
    if(len(sdict) == nb_unit_per_subdict):
      res.append(sdict)
      to_append = False
      sdict = {}

  if(to_append == True):
    res.append(sdict)
  
  return res 

def convertScoreToList(scores, probes):
  ret = []
  i = 0
  for k in sorted(probes.keys()):
    ret.append((probes[k][1], probes[k][2], probes[k][3], probes[k][4], scores[i]))
    i+=1
  return ret

def probes_used_generate_vector(probe_files_full, probe_files_model):
  """Generates boolean matrices indicating which are the probes for each model"""
  C_probesUsed = numpy.ndarray(len(probe_files_full), 'bool')
  C_probesUsed.fill(False)
  c=0 
  for k in sorted(probe_files_full.keys()):
    if probe_files_model.has_key(k): C_probesUsed[c] = True
    c+=1
  return C_probesUsed

def probes_used_extract_scores(full_scores, same_probes):
  """Extracts a matrix of scores for a model, given a probes_used row vector of boolean"""
  if full_scores.extent(1) != same_probes.extent(0): raise "Size mismatch"
  model_scores = numpy.ndarray((full_scores.extent(0),same_probes.count()), 'float64')
  c=0
  for i in range(0,full_scores.extent(1)):
    if same_probes[i]:
      for j in range(0,full_scores.extent(0)):
        model_scores[j,c] = full_scores[j,i]
      c+=1
  return model_scores 
