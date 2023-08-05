# -*- coding: utf-8 -*-
"""
grape.recipe.pipeline
"""
from setuptools import setup, find_packages

version = '1.1.13'

long_description = """The grape.recipe.pipeline package is a Buildout recipe used for
configuring Grape, a pipeline used for processing and analyzing RNA-Seq data.
RNA-Seq is a next generation sequencing technology used to sequence cellular RNA.
To run Grape, you need the read files in Fasta, FastQ or prealigned SAM/BAM formats,
as well as a genome and a gene transcript annotation. First, Grape does the quality 
control and then aligns the reads to the genome. The core of Grape is the analysis of
the transcriptome. Grape quantifies Gene and transcript expression levels, estimates 
exon inclusion levels, and discovers novel splice forms for you, and includes a powerful
web application that allows you to seamlessly publish your summary statistics locally 
or on the Internet. 
While Grape can run on a standalone machine with modest hardware requirements, it is 
designed to run in parallel on a computer cluster. Grape comes with its own default 
mapping and quantification tools, and makes it easy to replace any of these tools with 
your own, given that they support popular data interchange formats. Grape is being actively
developed at the CRG, and is used in dozens of projects with massive datasets, 
like the Illumina Body Map Project (HBM) and the ENCODE project."""
entry_point = 'grape.recipe.pipeline:Recipe'
entry_points = {"zc.buildout": [
                  "default = grape.recipe.pipeline:Recipe",
               ]}

setup(name='grape.recipe.pipeline',
      version=version,
      description="A Buildout recipe installing Grape RNA-Seq pipelines",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Buildout',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Operating System :: POSIX :: Linux',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: System :: Installation/Setup'],
      keywords='RNA-Seq pipeline ngs transcriptome bioinformatics',
      author='Maik Roder',
      author_email='maikroeder@gmail.com',
      url='http://big.crg.cat/services/grape',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['grape', 'grape.recipe'],
      include_package_data=True,
      zip_safe=False,
      test_suite='grape.recipe.pipeline.tests',
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
