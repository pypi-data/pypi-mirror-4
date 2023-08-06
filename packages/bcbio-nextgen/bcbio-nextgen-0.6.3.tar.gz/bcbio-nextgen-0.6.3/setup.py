#!/usr/bin/env python
"""Setup file and install script for NextGen sequencing analysis scripts.
"""
from setuptools import setup, find_packages

setup(name = "bcbio-nextgen",
      version = "0.6.3",
      author = "Brad Chapman",
      author_email = "chapmanb@50mail.com",
      description = "Best-practice pipelines for fully automated high throughput sequencing analysis",
      license = "MIT",
      url = "https://github.com/chapmanb/bcbio-nextgen",
      namespace_packages = ["bcbio"],
      packages = find_packages(),
      package_data={'bcbio': ['bam/data/*']},
      scripts = ['scripts/bcbio_nextgen.py',
                 'scripts/bam_to_wiggle.py',
                 'scripts/barcode_sort_trim.py',
                 'scripts/illumina_finished_msg.py',
                 'scripts/nextgen_analysis_server.py',
                 'scripts/solexa_qseq_to_fastq.py',
                 ],
      install_requires = [
          "boto >= 2.8.0",
          "cutadapt >= 1.2.1",
          "psutil >= 0.6.1",
          "biopython >= 1.61",
          "Mako >= 0.3.6",
          "PyYAML >= 3.09",
          "sh >= 1.07",
          "Logbook >= 0.3",
          "Cython >= 0.17.3",
          "pysam >= 0.7",
          "fabric >= 1.5",
          "ipython-cluster-helper >= 0.1.2",
          "pyzmq == 2.2.0.1",
          "ipython >= 0.13.1",
          "bioblend >= 0.2.2",
          "pybedtools >= 0.6.2",
          "py_descriptive_statistics >= 0.2",
          "paramiko >= 1.9.0",
          "celery >= 2.2.7,<3.0.0",
          #"rpy2 >= 2.0.7"
      ])
