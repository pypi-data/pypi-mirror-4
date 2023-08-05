Welcome to grape.recipe.pipeline's documentation!
=================================================

Grape (Grape RNA-Seq Analysis Pipeline Environment) is a pipeline for processing
and analyzing RNA-Seq data developed at the Bioinformatics and Genomics unit of
the Centre for Genomic Regulation (CRG) in Barcelona. 

The grape.buildout packages makes use of the grape.recipe.pipeline recipe
to configure Grape pipelines. You get preconfigured start and execute scripts, 
and don't have to worry about command line options any more. This takes the pain
out of configuring multiple Grape pipelines.

To learn more about Grape, and to download and install it, go to the Bioinformatics 
and Genomics website at:

`Grape Homepage <http://big.crg.cat/services/grape>`_ 

.. note::

    The grape.recipe.pipeline package is a Buildout recipe used by grape.buildout, 
    and is not a standalone Python package. It is only going to be useful as installed by the 
    grape.buildout package.


Motivation
----------

Here at the CRG, we configure all our RNASeq pipeline runs in a central place
before running the Grape pipelines. Once all the accessions and pipeline
profiles have been defined and the buildout parts have been created, we start
and execute them.

When we receive Fastq or bam files for a project, we typically have to:

1. Define the accessions and profiles in::

    grape.buildout/accessions/MyProject/db.cfg
    grape.buildout/profiles/MyProject/db.cfg

2. Create a pipeline project folder in::

    grape.buildout/pipelines/MyProject

3. Configure the buildout in::

    grape.buildout/pipelines/MyProject/buildout.cfg

4. Run the buildout in::

    grape.buildout/pipelines/MyProject

5. Run the pipelines in::

    grape.buildout/pipelines/MyProject/parts/*/

The grape.recipe.pipeline recipe plays a major role in step number 4. 
The buildout uses the recipe to produce the individual pipelines and 
preconfigure the start and execute scripts with all the necessary command 
line options.

Configuration
-------------

Here's a complete example of how the pipelines are configured, taken from the
Test project in grape.buildout.

First we define an accession in::

    accession/Test/db.cfg

This is the content of the db.cfg file::

  [TestRun]
  species = Homo sapiens
  readType = 2x76
  cell=NHEK
  rnaExtract=LONGPOLYA
  localization=CELL
  replicate=1
  qualities=solexa
  type=fastq
  file_location = ${buildout:directory}/src/testdata/testA.r2.fastq.gz
                  ${buildout:directory}/src/testdata/testA.r1.fastq.gz
                  ${buildout:directory}/src/testdata/testB.r2.fastq.gz
                  ${buildout:directory}/src/testdata/testB.r1.fastq.gz
  sample = Test_TestLocaltrun_read_stats_sample_testA.2
           Test_TestLocaltrun_read_stats_sample_testA.1
           Test_TestLocaltrun_read_stats_sample_testB.2
           Test_TestLocaltrun_read_stats_sample_testB.1
  mate_id = testA.2
            testA.1
            testB.2
            testB.1
  pair_id = testA
            testA
            testB
            testB
  label = Test
          Test
          Test
          Test
  type = fastq

Then we need to define the pipeline runs in::

    profiles/MyProject/db.cfg

This is the content of the db.cfg file::

  [runs]
  parts = TestRun

  [pipeline]
  TEMPLATE   = ${buildout:directory}/src/pipeline/template3.0.txt
  PROJECTID  = Test
  DB         = Test_RNAseqPipeline
  COMMONDB   = Test_RNAseqPipelineCommon
  THREADS    = 8
  MAPPER     = GEM
  MISMATCHES = 2
  CLUSTER    = mem_6
  ANNOTATION = ${buildout:directory}/src/testdata/H.sapiens.EnsEMBL.55.test.gtf
  GENOMESEQ  = ${buildout:directory}/src/testdata/H.sapiens.genome.hg19.test.fa

  [TestRun]
  recipe=grape.recipe.pipeline
  accession = TestRun

Now that we have the accessions and profiles defined, we can go to our project
folder and define the buildout.cfg that will produce our Grape pipelines::

    pipelines/Test/buildout.cfg
    
The buildout.cfg should look like this::

  [buildout]
  extends = ../dependencies.cfg
            ../../accessions/Test/db.cfg
            ../../profiles/Test/db.cfg

There are pointers to the accession and profile. The dependencies file takes
care of installing all the dependencies, like overlap, flux, gem, and the
Grape pipeline. 

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

