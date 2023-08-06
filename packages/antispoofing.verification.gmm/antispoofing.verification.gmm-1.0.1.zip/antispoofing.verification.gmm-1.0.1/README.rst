=============================================================
 Parts-Based GMM Verification for the Replay Attack Database
=============================================================

This `Bob`_ satellite package allows you to run a baseline Parts-Based GMM face
verification system on the Replay Attack Database. It explains how to setup
this package, generate the Universal Background Model (UBM), client models and
finally, scores.

If you use this package and/or its results, please cite the following
publications:

1. The Replay-Attack Database and baseline GMM results for it::

    @inproceedings{Chingovska_BIOSIG_2012,
      author = {I. Chingovska AND A. Anjos AND S. Marcel},
      keywords = {Attack, Counter-Measures, Counter-Spoofing, Face Recognition, Liveness Detection, Replay, Spoofing},
      month = sep,
      title = {On the Effectiveness of Local Binary Patterns in Face Anti-spoofing},
      booktitle = {IEEE BioSIG 2012},
      year = {2012},
    }

2. Bob as the core framework used for these results::

    @inproceedings{Anjos_ACMMM_2012,
        author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
    }

If you wish to report problems or improvements concerning this code, please
contact the authors of the above mentioned papers.

Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.verification.gmm
  <http://pypi.python.org/pypi/antispoofing.verification.gmm>`_ to download the
  latest stable version of this package.

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install antispoofing.verification.gmm

You can also do the same with ``easy_install``::

  $ easy_install antispoofing.verification.gmm

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/antispoofing.verification.gmm>`_ and unpack it in
your working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob`_, <you must make
  sure that the ``bootstrap.py`` script is called with the **same** interpreter
  used to build Bob, or unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``external`` and edit the
  line ``egg-directories`` to point to the ``lib`` directory of the Bob
  installation you want to use. For example::

    [external]
    recipe = xbob.buildout:external
    egg-directories=/Users/crazyfox/work/bob/build/lib

User Guide
----------

Configuration Tweaking (optional)
=================================

The current scripts have been tunned to reproduce the results presented on some
of our publications (as indicated above), as well as on FP7 Project `TABULA
RASA <http://www.tabularasa-euproject.org/>`_ reports.  They still accept an
alternate (python) configuration file that can be passed as input. If nothing
is passed, a default configuration file located at
``antispoofing/verification/gmm/config/gmm_replay.py`` is used. Copy that file
to the current directory and edit it to modify the overall configuration for
the mixture-model system or for the (DCT-based) feature extraction. Use the
option ``--config=myconfig.py`` to set your private configuration if you decide
to do so. Remember to set the option thoroughly through out all script calls or
unexpected results may happen.

Running the Experiments
=======================

Follow the sequence described here to reproduce paper results.

Run ``feature_extract.py`` to extract the DCT block features. This step is
the only that requires the original database videos as input. It will generate,
**per video frame**, all input features required by the scripts that follow
this one::

  $ ./bin/feature_extract.py /root/of/replay/attack/database results/dct

This will run through the 1300 videos in the database and extract the features
at the frame intervals defined at the configuration. In a relatively fast
machine, it will take about 10-20 seconds per input video, with a frame-skip
parameter set to 10 (the default). If you want to be thorough, you will need to
parallelize this script so that the overall database can be processed in a
reasonable amount of time.

You can parallelize the execution of the above script (and of some of the
scripts below as well) if you are a Idiap. Just do the following instead::

  $ ./bin/jman submit --array=1300 ./bin/feature_extract.py /root/of/replay/attack/database results/dct --grid

Notice the ``--array=1300`` and ``--grid`` option by the end of the script. The
above instruction tells SGE to run 1300 versions of my script with the same
input parameters. The only difference is ``SGE_TASK_ID`` environment variable
that is changed at every interation (thanks to the ``--array=1300`` option).
The ``--grid`` option the execution of the script analyze first the value of
``SGE_TASK_ID`` and re-set the internal processing so that particular instance
of ``feature_extract.py`` only processes one of the 1300 videos that requires
processing. You can check the status of the jobs in the grid with ``jman
refresh`` (refer to the `GridTk manual <http://packages.python.org/gridtk>` for
details).

.. note::

  If you are not, you can still take a look at our `GridTk package
  <http://pypi.python.org/pypi/gridtk>`_ for a logging grid job manager for SGE.

UBM Training
============

Run ``train_ubm.py`` to create the GMM Universal Background Model from selected
features (in the enrollment/training subset)::
  
  $ ./bin/train_ubm.py results/dct results/ubm.hdf5

.. note::

  Note: if you use ~1k files, it will take a few hours to complete and there is
  currently no way to parallelize this.  This step requires all features for
  the training set/enrollment are calculated. The job can take many gigabytes
  of physical memory from your machine, so we advise you to run it in a machine
  with, at least, 8 gigabytes of free memory.

Unfortunately, you cannot easily parallelize this job. Nevertheless, you can
submit it to the grid with the following command and avoid it to run on your
machine (nice if you have a busy day of work)::

  $ ./bin/jman submit --queue=q_1week --memory=8G ./bin/train_ubm.py results/dct results/ubm.hdf5

Even if you choose a long enough queue, it is still prudent to set the memory
requirements for the node you will be assigned to, to guarantee a minimum
amount of memory.

UBM Statistics Generation
=========================

Run ``generate_statistics.py`` to create the background statistics for all
datafiles so we can calculate scores later. This step requires that the UBM is
trained and all features are available::

  $ ./bin/generate_statistics.py results/dct results/ubm.hdf5 results/stats

This will take a lot of time to go through all the videos in the replay
database. You can optionally submit the command to the grid, if you are at
Idiap, with the following::

  $ ./bin/jman submit --array=840 ./bin/generate_statistics.py results/dct results/ubm.hdf5 results/stats --grid

This command will spread the GMM UBM statistics calculation over 840 processes
that will run in about 5-10 minutes each. So, the whole job will take a few
hours to complete - taking into consideration current settings for SGE at
Idiap.

Client Model training
=====================

.. note::

  You can do this in parallel with the step above as it only depends on the
  input features pre-calculated at step 3

Generate the models for all clients::

  $ ./bin/enrol.py results/dct results/ubm.hdf5 results/models

If you think the above job is too slow, you can throw it at the grid as well::

  $ ./bin/jman submit --array=35 ./bin/enrol.py results/dct results/ubm.hdf5 results/models --grid

Scoring
=======

In this step you will score the videos (every N frames up to a certain frame
number) against the generated client models. We do this exhaustively for both
the test and development data. Command line execution goes like this::

  $ ./bin/score.py results/stats results/ubm.hdf5 results/models results/scores

Linear scoring is fast, but you can also submit a client-based break-down of
this problem like this::

  $ ./bin/jman submit --array=35 ./bin/score.py results/stats results/ubm.hdf5 results/models results/scores --grid

Full Score Files
================

After scores are calculated, you need to put them together to setup development
and test text files in a 4 or 5 column format. To do that, use the application
``build_score_files.py``. The next command will generate the baseline
verification results by thouroughly matching every client video against every
model available in the individual sets, averaging over (the first) 220 frames::

  $ ./bin/build_score_files.py results/scores results/perf --thorough --frames=220

You can specify to use the attack protocols like this (avoid using the
`--thourough` option)::

  $ ./bin/build_score_files.py results/scores results/perf --protocol=grandtest --frames=220

.. warning::

  It is possible you see warnings being emitted by the above programs in
  certain cases. This is **normal**. The warnings correspond to cases in which
  the program is trying to collect data from a certain frame number in which a
  face was not detected on the originating video.

Reproduce Paper Results
=======================

To reproduce our paper results (~82% of attacks passing the verification
system), you must generate two score files as defined above and then call a few
programs that compute the threshold on the development set and apply it to the
licit and spoofing test sets::

  $ ./bin/eval_threshold.py --scores=results/perf/devel-baseline-thourough-220.4c
  Threshold: 0.686207566
  FAR : 0.000% (0/840)
  FRR : 0.000% (0/60)
  HTER: 0.000%

  $ ./bin/apply_threshold.py --scores=results/perf/test-grandtest-220.4c --threshold=0.686207566
  FAR : 82.500% (330/400)
  FRR : 0.000% (0/80)
  HTER: 41.250%

.. some links

.. _bob: http://idiap.github.com/bob
