=====================
grape.recipe.pipeline
=====================
---------------------------------------------
Configure a Grape pipeline in one simple step
---------------------------------------------

**grape.recipe.pipeline** prepares everything that is needed to run Grape
pipelines so you don't have to write any command line options.

Background
==========

Grape (Grape RNA-Seq Analysis Pipeline Environment) is a pipeline for processing
and analyzing RNA-Seq data developed at the Bioinformatics and Genomics unit of
the Centre for Genomic Regulation (CRG) in Barcelona. 

Important Note
==============

The grape.recipe.pipeline package is a Buildout recipe used by Grape, and is not
a standalone Python package. It is only going to be useful as installed
by the grape.buildout package.

To learn more about Grape, and to download and install it, go to the Bioinformatics 
and Genomics website at:

http://big.crg.cat/services/grape

Motivation
==========

Here at the CRG, we configure all our RNASeq pipeline runs in a central place
before running the Grape pipelines. Once all the accessions and pipeline
profiles have been defined and the buildout parts have been created, we start
and execute them.

When we receive Fastq or bam files for a project, we typically have to:

1. Define the accessions and profiles in 

    grape.buildout/accessions/MyProject/db.cfg
    grape.buildout/profiles/MyProject/db.cfg

2. Create a pipeline project folder in grape.buildout/pipelines/MyProject

3. Configure the buildout in grape.buildout/pipelines/MyProject/buildout.cfg

4. Run the buildout in grape.buildout/pipelines/MyProject

5. Run the first pipelines in grape.buildout/pipelines/MyProject/parts/*/

Using this approach, we can batch run any number of pipelines and never have to
think about the command line options.

Installation
============

The grape.recipe.pipeline package is already installed by grape.buildout, so
you don't have to do this. 

If you want to install it as part of a buildout, you would have to add this
configuration to the buildout::

  [buildout]
  parts = grape.recipe.pipeline
  eggs = grape.recipe.pipeline

  [grape.recipe.pipeline]
  recipe = hexagonit.recipe.download
  url = http://big.crg.cat/~mroder/grape/grape.recipe.pipeline-1.1.tar.gz
  md5sum = 5bd87d4d56a61b019ccc854f040f1d6d
  destination = src/grape.recipe.pipeline
  strip-top-level-dir = true
  hash-name = false

Then you can use this recipe like this::

  [runs]
  parts = TestRun

  [pipeline]
  ... pipeline configuration omitted for brevity ...

  [TestRun1]
  recipe=grape.recipe.pipeline
  accession = TestRun1


Configuration
=============

Here's a complete example of how the pipelines are configured, taken from the
Test project in grape.buildout.

First we define an accession in accession/Test/db.cfg::

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

Then we need to define pipeline run and in profiles/MyProject/db.cfg::

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

The pipelines/Test/buildout.cfg looks like this::

  [buildout]
  extends = ../dependencies.cfg
            ../../accessions/Test/db.cfg
            ../../profiles/Test/db.cfg

There are pointers to the accession and profile. The dependencies file takes
care of installing all the dependencies, like overlap, flux, gem, and the
Grape pipeline. It also installs grape.recipe.pipeline, as describe in the
above Installation section.