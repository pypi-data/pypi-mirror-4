"""
Test for prepare.py
"""

import os
import unittest
import shutil
import tempfile

from grape.recipe.pipeline.prepare import main
from grape.recipe.pipeline.prepare import get_pipeline_script_command
from grape.recipe.pipeline.prepare import CUFFLINKS_BINARIES
from grape.recipe.pipeline.prepare import check_read_labels
from grape.recipe.pipeline.prepare import parse_trim_length
from grape.recipe.pipeline.prepare import parse_flux_mem


SANDBOX = tempfile.mkdtemp('buildoutSetUp')
PATH = os.path.join(SANDBOX, 'buildout')
OPTIONS = {'accession': 'TestRun',
           'location': os.path.join(PATH, 'parts/TestRun'),
           }
BUILDOUT = {}
FILE_LOCATIONS = [os.path.join(PATH, "src/testdata/testA.r2.fastq.gz"),
                  os.path.join(PATH, "src/testdata/testA.r1.fastq.gz"),
                  os.path.join(PATH, "src/testdata/testB.r2.fastq.gz"),
                  os.path.join(PATH, "src/testdata/testB.r1.fastq.gz")]
BUILDOUT['TestRun'] = {'paired': '1',
                       'file_location': '\n'.join(FILE_LOCATIONS),
                       'species': 'Homo sapiens',
                       'readType': '2x76',
                       'cell': 'NHEK',
                       'rnaExtract': 'LONGPOLYA',
                       'localization': 'CELL',
                       'qualities': 'solexa',
                       'pair_id': 'testA\ntestA\ntestB\ntestB',
                       'mate_id': 'testA.2\ntestA.1\ntestB.2\ntestB.1',
                       'label': 'Test\nTest\nTest\nTest',
                       'type': 'fastq',
                       'replicate': '1'
                       }
TEMPLATE = os.path.join(PATH, "/src/pipeline/TEMPLATE3.0.txt")
GENOME = os.path.join(PATH, "/src/testdata/H.sapiens.genome.hg19.test.fa")
ANNOTATION = os.path.join(PATH, "/src/testdata/H.sapiens.EnsEMBL.55.test.gtf")
BUILDOUT['pipeline'] = {'TEMPLATE': TEMPLATE,
                        'PROJECTID': 'Test',
                        'THREADS': '2',
                        'DB': 'TestRNAseqPipeline',
                        'COMMONDB': 'TestRNAseqPipelineCommon',
                        'MAPPER': 'GEM',
                        'MISMATCHES': '2',
                        'GENOMESEQ': GENOME,
                        'ANNOTATION': ANNOTATION,
                        'MAXINTRONLENGTH': 50000,
                        'CLUSTER': 'mem_6',
                        'HOST': 'pou',
                        'PREPROCESS': '${buildout:directory}/scripts/pre.pl',
                        'PREPROCESS_TRIM_LENGTH': '24',
                        'MIN_RECURSIVE_MAPPING_TRIM_LENGTH': '20',
                        'FLUXMEM': '16G'
                        }

BUILDOUT['buildout'] = {'directory': PATH}
BUILDOUT['settings'] = {'java': '',
                        'flux_jar': '',
                        'overlap': os.path.join(PATH, 'src/overlap/overlap'),
                        'gem_folder': os.path.join(PATH, 'src/gem'),
                        }
SCRIPT = ["#!/bin/bash\nbin/start_RNAseq_pipeline.3.0.pl",
          "-species",
          "'Homo",
          "sapiens'",
          "-genome",
          "/src/testdata/H.sapiens.genome.hg19.test.fa",
          "-annotation",
          "/src/testdata/H.sapiens.EnsEMBL.55.test.gtf",
          "-project",
          "Test",
          "-experiment",
          "TestRun",
          "-template",
          "/src/pipeline/TEMPLATE3.0.txt",
          "-readlength",
          "76",
          "-cellline",
          "'NHEK'",
          "-rnafrac",
          "LONGPOLYA",
          "-compartment",
          "CELL",
          "-bioreplicate",
          "1",
          "-threads",
          "2",
          "-qualities",
          "solexa",
          "-cluster",
          "mem_6",
          "-database",
          "TestRNAseqPipeline",
          "-commondb",
          "TestRNAseqPipelineCommon",
          "-host",
          "pou",
          "-mapper",
          "GEM",
          "-mismatches",
          "2",
          "-maxintronlength",
          "50000",
          "-preprocess",
          "'${buildout:directory}/scripts/pre.pl'",
          "-preprocess_trim_length",
          "24",
          "-trimlength",
          "20",
          "-fluxmem",
          "16G"]


class MainTests(unittest.TestCase):
    """
    Test the main method in prepare.py
    """

    def setUp(self):  # pylint: disable=C0103
        shutil.rmtree(PATH, ignore_errors=True)
        os.mkdir(PATH)
        os.mkdir(os.path.join(PATH, 'bin'))
        os.mkdir(os.path.join(PATH, 'parts'))
        os.mkdir(os.path.join(PATH, 'parts/TestRun'))
        os.mkdir(os.path.join(PATH, 'src'))
        os.mkdir(os.path.join(PATH, 'src/flux'))
        os.mkdir(os.path.join(PATH, 'src/flux/bin'))
        path = open(os.path.join(PATH, 'src/flux/bin/flux'), 'w')
        path.close()
        os.mkdir(os.path.join(PATH, 'src/gem'))
        os.mkdir(os.path.join(PATH, 'src/overlap'))
        path = open(os.path.join(PATH, 'src/overlap/overlap'), 'w')
        path.close()
        cufflinks_path = os.path.join(PATH, 'src/cufflinks')
        os.mkdir(cufflinks_path)
        for cuffbin in CUFFLINKS_BINARIES:
            path = open(os.path.join(cufflinks_path, cuffbin), 'w')
            path.close()
        os.mkdir(os.path.join(PATH, 'src/pipeline'))
        os.mkdir(os.path.join(PATH, 'src/pipeline/bin'))
        os.mkdir(os.path.join(PATH, 'src/pipeline/lib'))
        os.mkdir(os.path.join(PATH, 'src/testdata'))
        path = open(os.path.join(PATH,
                                 'src/testdata/testA.r1.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(PATH,
                                 'src/testdata/testA.r2.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(PATH,
                                 'src/testdata/testB.r1.fastq.gz'), 'w')
        path.close()
        path = open(os.path.join(PATH,
                                 'src/testdata/testB.r2.fastq.gz'), 'w')
        path.close()
        os.mkdir(os.path.join(PATH, 'var'))

    def test_main(self):
        """
        Test the main method
        """
        os.chdir(PATH)
        if os.path.exists('src/fastqc'):
            os.remove('src/fastqc')
        os.makedirs('src/fastqc')
        fastqc = open('src/fastqc/fastqc', 'w')
        perl_code = ('#!/soft/bin/perl', 'use warnings;')
        fastqc.write('\n'.join(perl_code))
        fastqc.close()

        if os.path.exists('src/pipeline/bin'):
            os.removedirs('src/pipeline/bin')
        os.makedirs('src/pipeline/bin')

        overlap_path = os.path.join(PATH, 'overlap')
        overlap = open(overlap_path, 'w')
        overlap.write('dummy')
        overlap.close()

        buildout = BUILDOUT.copy()
        buildout['settings'] = {'perl': '/soft/bin/perl',
                                'overlap': overlap_path,
                                'gem_folder': PATH,
                                'nextgem_folder': PATH}
        result = main(OPTIONS.copy(), buildout)
        self.failUnless(result is None)


class PipelineScriptTests(unittest.TestCase):
    """
    Test the part producing the pipeline scripts.
    """

    def test_command(self):
        """
        Test the get_pipeline_script_command
        """
        os.chdir(PATH)
        buildout = BUILDOUT.copy()
        accession = buildout['TestRun']
        pipeline = BUILDOUT['pipeline'].copy()
        options = OPTIONS.copy()
        options['experiment_id'] = os.path.split(options['location'])[-1]
        command = get_pipeline_script_command(accession, pipeline, options)
        self.failUnless(command.split(' ') == SCRIPT, command.split(' '))

    def test_more_options(self):
        """
        Test the get_pipeline_script_command method with replicate and other
        options.
        """
        os.chdir(PATH)
        buildout = BUILDOUT.copy()
        accession = buildout['TestRun']
        accession['replicate'] = '1'
        pipeline = BUILDOUT['pipeline'].copy()
        pipeline['HOST'] = 'dummyhost'
        pipeline['PREPROCESS'] = 'dummypreprocess'
        pipeline['PREPROCESS_TRIM_LENGTH'] = 'dummytrimlength'
        options = OPTIONS.copy()
        options['experiment_id'] = os.path.split(options['location'])[-1]
        options['description'] = 'dummydescription'
        command = get_pipeline_script_command(accession, pipeline, options)
        self.failUnless(" -bioreplicate 1 " in command)
        self.failUnless(" -host dummyhost " in command)
        self.failUnless(" -run_description 'dummydescription' " in command)
        self.failUnless(" -preprocess 'dummypreprocess' " in command)
        self.failUnless(" -preprocess_trim_length dummytrimlength" in command)

    def test_empty_cluster(self):
        """
        Test the get_pipeline_script_command method with empty cluster
        """
        os.chdir(PATH)
        buildout = BUILDOUT.copy()
        accession = buildout['TestRun']
        pipeline = BUILDOUT['pipeline'].copy()
        pipeline['CLUSTER'] = ''
        options = OPTIONS.copy()
        options['experiment_id'] = os.path.split(options['location'])[-1]
        self.failUnlessRaises(AttributeError,
                              get_pipeline_script_command,
                              accession,
                              pipeline,
                              options)

    def test_cluster_given(self):
        """
        Test the get_pipeline_script_command method with cluster
        """
        os.chdir(PATH)
        buildout = BUILDOUT.copy()
        accession = buildout['TestRun']
        pipeline = BUILDOUT['pipeline'].copy()
        pipeline['CLUSTER'] = 'dummy'
        options = OPTIONS.copy()
        options['experiment_id'] = os.path.split(options['location'])[-1]
        command = get_pipeline_script_command(accession, pipeline, options)
        self.failUnless(" -cluster dummy " in command)


class ReadLabelsTests(unittest.TestCase):
    """
    Test the check_read_labels method.
    """

    def test_no_paired_given(self):
        """
        Test the check_read_labels method with a non existing paired attribute
        """
        acc = {}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_not_paired_dummy(self):
        """
        Test the check_read_labels method with non paired
        """
        accession = {'paired': '0', 'pair_id': '', 'mate_id': '', 'label': ''}
        check_read_labels(accession, 'dummy')

    def test_paired_dummy(self):
        """
        Test the check_read_labels method with paired
        """
        accession = {'paired': '1',
                     'pair_id': '1\n1',
                     'mate_id': '',
                     'label': ''}
        check_read_labels(accession, 'dummy')

    def test_wrong_paired_dummy(self):
        """
        Test the check_read_labels method with paired
        """
        acc = {'paired': '2', 'pair_id': '', 'mate_id': '', 'label': ''}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_not_paired_mate_and_pair_same_1(self):
        """
        When not paired, mate_id and pair_id must be the same
        """
        acc = {'paired': '0', 'pair_id': '1', 'mate_id': '2', 'label': ''}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_not_paired_mate_and_pair_same_2(self):
        """
        All labels should be the same
        """
        acc = {'paired': '0', 'pair_id': '1', 'mate_id': '1', 'label': '1\n2'}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_not_all_mate_ids_different(self):
        """
        All mate_ids must be different
        """
        acc = {'paired': '0',
               'pair_id': '1\n1',
               'mate_id': '1\n1',
               'label': '1\n1'}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_paired_where_pairs_not_paired_with_2(self):
        """
        Test the check_read_labels method where the pairs are not paired.
        Try two lines.
        """
        acc = {'paired': '1', 'pair_id': '1\n2', 'mate_id': '', 'label': ''}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_paired_where_pairs_not_paired_with_4(self):
        """
        Test the check_read_labels method where the pairs are not paired
        Try four lines.
        """
        acc = {'paired': '1',
               'pair_id': '1\n2\n3\n4',
               'mate_id': '',
               'label': ''}
        self.assertRaises(AttributeError, check_read_labels, acc, 'dummy')

    def test_parse_trim_length(self):
        """
        Test parsing of the trim length works for integers.
        """
        pipeline = {'MIN_RECURSIVE_MAPPING_TRIM_LENGTH': '40'}
        self.failUnless(parse_trim_length(pipeline) == '40')

    def test_parse_flux_mem(self):
        """
        Test that an integer value for fluxmem works
        """
        pipeline = {'FLUXMEM': '16'}
        self.failUnless(parse_flux_mem(pipeline) == '16')

    def test_parse_flux_mem_gigabyte(self):
        """
        Test that a number plus G works, like 16G returns 16.
        """
        pipeline = {'FLUXMEM': '16'}
        self.failUnless(parse_flux_mem(pipeline) == '16')


def test_suite():
    """
    Run the test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
