from setuptools import setup, find_packages

setup(
    name='antispoofing.verification.gmm',
    version='1.0.1',
    description='Replay-Attack Face Verification Package Based on a Parts-Based Gaussian Mixture Models',
    url='http://pypi.python.org/pypi/antispoofing.verification.gmm',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "antispoofing",
      "antispoofing.verification",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.0.0, < 1.1.0",
      ],


    entry_points={
      'console_scripts': [
        'feature_extract.py = antispoofing.verification.gmm.script.feature_extract:main',
        'train_ubm.py = antispoofing.verification.gmm.script.train_ubm:main',
        'generate_statistics.py = antispoofing.verification.gmm.script.generate_statistics:main',
        'enrol.py = antispoofing.verification.gmm.script.enrol:main',
        'score.py = antispoofing.verification.gmm.script.score:main',
        'build_score_files.py = antispoofing.verification.gmm.script.build_score_files:main',
        'apply_threshold.py = bob.measure.script.apply_threshold:main',
        'eval_threshold.py = bob.measure.script.eval_threshold:main',
        'compute_perf.py = bob.measure.script.compute_perf:main',
        ],
      },

    )
