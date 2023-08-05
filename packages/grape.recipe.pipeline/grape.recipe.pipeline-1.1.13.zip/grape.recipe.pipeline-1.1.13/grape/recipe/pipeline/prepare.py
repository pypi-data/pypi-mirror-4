"""
This module is used by buildout when building the RNASeq pipeline parts:

    [shortRNA001C]
    recipe = grape.recipe.pipeline
    accession = shortRNA001C
    pipeline = male

The accession attribute is necessary so that the corresponding files and
metadata for the pipeline run can be found in the accession database.

The pipeline attribute specifies the section defining the pipeline options.
"""

import os
import shutil
import glob

CUFFLINKS_BINARIES = ('cuffcompare',
                      'cuffdiff',
                      'cufflinks',
                      'cuffmerge',
                      'gffread',
                      'gtf_to_sam')


class InstallationState:
    """
    The var/pipeline/bin and var/pipeline/var folders have to be reinstalled
    only once for the first part that gets installed. All of the following
    parts do not have to reinstall the contents of these folders.
    """

    state = {}

    def __init__(self):
        """Reset the installation state"""
        self.state = {}

    def set_reinstall(self, path):
        """Call when the path has been reinstalled"""
        self.state[path] = True

    def get_reinstall(self, path):
        """Call when you need to know whether the path has been reinstalled."""
        return self.state.get(path, False)

INSTALLATION_STATE = InstallationState()


def install_bin_folder(options, buildout, bin_folder):
    """
    The bin folder from src/pipeline/bin is copied to var/pipeline/bin
    Then each part gets a soft link.

    The bin folder is made available globally to all pipelines
    in var/pipeline/bin
    The shebang of all contained scripts has to be changed to use the Perl
    version defined in buildout.cfg
    """
    # Start with a fresh installation once
    if not INSTALLATION_STATE.get_reinstall(bin_folder):
        shutil.rmtree(bin_folder, ignore_errors=True)
        # The original code comes from the SVN
        buildout_directory = buildout['buildout']['directory']
        svn_folder = 'src/pipeline/bin'
        pipeline_bin_folder = os.path.join(buildout_directory, svn_folder)
        # The bin folder is populated from the SVN version of the bin folder
        shutil.copytree(pipeline_bin_folder, bin_folder)

    # The bin folder of the current part should point to the global bin folder
    target = os.path.join(options['location'], 'bin')
    if os.path.exists(target):
        os.remove(target)
    # Make a symbolic link to the global bin folder in var/pipeline in the
    # part
    os.symlink(bin_folder, target)
    if not os.path.exists(target):
        raise AttributeError(target)

    if not INSTALLATION_STATE.get_reinstall(bin_folder):
        # Use the same shebang for all perl scripts
        perlscripts = os.path.join(bin_folder, '*.pl')
        for perl_script in glob.glob(perlscripts):
            perl_script_path = os.path.join(bin_folder, perl_script)
            patch_perl_script(buildout, perl_script_path)


def patch_perl_script(buildout, perl_script_path):
    """
    The shebang contained in perl scripts is changed to use the perl version
    configured in the settings section of the buildout.
    """
    custom_shebang = "#!%s\n" % buildout['settings']['perl']
    perl_file = open(perl_script_path, 'r')
    # Just the read the first line, which is expected to be the shebang
    shebang = perl_file.readline().strip()
    # The shebang is already ok, so just return
    if shebang == custom_shebang:
        perl_file.close()
        return
    # Make sure the shebang is as expected
    if (not shebang.startswith('#!')) or (not 'perl' in shebang):
        print "Expected script to start with #! and include the string 'perl'"
        print "This one (%s) starts with %s" % (perl_script_path, shebang)
        raise AttributeError
    # Read the rest of the file only, omitting the shebang
    content = perl_file.read()
    perl_file.close()
    # Open the file again, this time for writing
    perl_file = open(perl_script_path, 'w')
    # Write the new shebang using our own perl version as defined in
    # the buildout.cfg
    perl_file.write(custom_shebang)
    # Write the rest of the content
    perl_file.write(content)
    perl_file.close()


def install_lib_folder(options, buildout, lib_folder):
    """
    The lib folder from src/pipeline/lib is copied to var/pipeline/lib
    Then each part gets a soft link.
    """
    buildout_directory = buildout['buildout']['directory']
    # Remove the old lib folder in var/pipeline

    if not INSTALLATION_STATE.get_reinstall(lib_folder):
        shutil.rmtree(lib_folder, ignore_errors=True)
        # The original lib folder is taken from the SVN
        svn_folder = 'src/pipeline/lib'
        pipeline_lib_folder = os.path.join(buildout_directory, svn_folder)
        # Copy the lib folder over to var/pipeline
        shutil.copytree(pipeline_lib_folder, lib_folder)

    # Make a symbolic link in the part to the lib folder in var/pipeline
    target = os.path.join(options['location'], 'lib')
    # Remove the old link
    if os.path.exists(target):
        os.remove(target)
    # And put in the new link
    os.symlink(lib_folder, target)
    if not os.path.exists(target):
        raise AttributeError(target)


def install_results_folder(options, results_folder):
    """
    Create a results folder in var for keeping the results of a pipeline run,
    and make a soft link to it in each part.
    """
    if os.path.exists(results_folder):
        pass
    else:
        os.mkdir(results_folder)
    target = os.path.join(options['location'], 'results')
    # Remove the old link
    if os.path.exists(target):
        os.remove(target)
    # And put in the new link
    os.symlink(results_folder, target)
    if not os.path.exists(target):
        raise AttributeError(target)


def install_gemindices_folder(options, gemindices_folder):
    """
    Create a GEMIndices folder for sharing the GEM Indices
    """
    if os.path.exists(gemindices_folder):
        pass
    else:
        os.mkdir(gemindices_folder)
    target = os.path.join(options['location'], 'GEMIndices')
    # Remove the old link
    if os.path.exists(target):
        os.remove(target)
    # And put in the new link
    os.symlink(gemindices_folder, target)
    if not os.path.exists(target):
        raise AttributeError(target)


def install_read_folder(options, accession):
    """
    Create a read folder with soft links to the read files
    """

    # Create the read folder in the parts folder
    read_folder = os.path.join(options['location'], 'readData')
    # There are only soft links in this folder, so the whole folder is deleted
    # every time.
    shutil.rmtree(read_folder, ignore_errors=True)
    # Now create the read folder
    os.mkdir(read_folder)
    number_of_reads = len(accession['file_location'].split('\n'))
    for number in range(0, number_of_reads):
        # Get the file location from the accession
        file_location = accession['file_location'].split('\n')[number].strip()
        # Try to recognize the url
        if file_location.startswith("http://"):
            # Unrecognized
            raise AttributeError
        # Only accept a path if it is inside of the path we expect.
        # This is so that tricks like ../ don't work
        if not os.path.exists(file_location):
            print "Warning! File does not exist: %s" % file_location
            continue
        # Make symbolic links to the read files
        # Take just the file name from the file location
        filename = os.path.split(file_location)[1]
        # Combine the read folder with the filename to get the target
        target = os.path.join(read_folder, filename)
        if os.path.exists(target):
            template = "Duplicated read files: \n%s"
            raise AttributeError(template % accession['file_location'])
        os.symlink(file_location, target)
        if not os.path.exists(target):
            raise AttributeError(target)


def check_read_labels(accession, experiment_id):
    """
    Make sure the labels are consistent with the paired information
    """
    if not 'paired' in accession:
        msg = "Experiment %s is missing the paired attribute."
        raise AttributeError(msg % experiment_id)
    if not accession['paired'] in ["0", "1"]:
        msg = "Wrong setting paired=%s in %s (Use paired=0 or paired=1)"
        info = (accession['paired'], experiment_id)
        raise AttributeError(msg % info)

    if accession['paired'] == '0':
        # For single end mate id and pair id have to be the same
        # So pair_id can be omitted for single end. if pair_id is missing
        # we don't complain
        if not accession['pair_id'] == accession['mate_id']:
            msg = "For unpaired, mate id and pair id have to be the same: %s."
            raise AttributeError(msg % experiment_id)
    elif accession['paired'] == '1':
        # pair id there can not be more that two values that are the same
        # e.g. three testA
        # For paired there are always 2 values that must be the same
        all_pairs = set(accession['pair_id'].split('\n'))
        if not len(all_pairs) * 2 == len(accession['pair_id'].split('\n')):
            # mate_id should all be different for paired and not paired
            msg = "The same pair_id must be used for exactly two lines: %s"
            raise AttributeError(msg % experiment_id)

    all_labels = set(accession['label'].split('\n'))
    if not len(all_labels) == 1:
        # Label should always be the same and should not be mixed
        # One line for the label is also possible
        msg = "All labels in the label attribute should be the same: %s"
        raise AttributeError(msg % experiment_id)

    all_mates = set(accession['mate_id'].split('\n'))
    if not len(all_mates) == len(accession['mate_id'].split('\n')):
        # mate_id should all be different for paired and not paired
        msg = "All mate ids need to be different: %s"
        raise AttributeError(msg % experiment_id)


def install_read_list(options, accession):
    """
    Add a read.list.txt in the part that will be used by the pipeline.
    """
    target = os.path.join(options['location'], 'read.list.txt')
    read_file = open(target, 'w')
    number_of_reads = len(accession['file_location'].split('\n'))
    for number in range(0, number_of_reads):
        labels = {}
        file_location = accession['file_location'].split('\n')[number]
        for attribute in ['pair_id', 'mate_id', 'label']:
            if attribute in accession:
                check_attribute(attribute, accession, number_of_reads)
                labels[attribute] = accession[attribute].split('\n')[number]
            else:
                template = "Specify a %s attribute for accession %s"
                message = template % (attribute, options['accession'])
                raise AttributeError(message)
        labels = readlist_labels(file_location, labels)
        read_file.write('\t'.join(labels))
        read_file.write('\n')
    read_file.close()


def check_attribute(attribute, accession, number_of_reads):
    """The attribute needs to have as many items as number of reads"""
    if len(accession[attribute].split('\n')) != number_of_reads:
        message = ["%s needs to have exactly one line for each " % attribute,
                   "file defined in file_locations in accession %s"]
        raise AttributeError("".join(message) % accession['accession'])


def readlist_labels(file_location, labels):
    """Validate the filename and"""
    file_name = os.path.split(file_location.strip())[1]
    if file_name.split('.')[-1] == "bam":
        pass
    elif file_name.split('.')[-1] == "gz":
        file_name = file_name[:-3]
    else:
        message = "Expecting .fastq file to be gzipped: %s"
        raise AttributeError(message % file_location)
    labels = (file_name.strip(),
              labels['pair_id'].strip().replace(' ', ''),
              labels['mate_id'].strip().replace(' ', ''),
              labels['label'].strip().replace(' ', ''))
    return labels


def install_dependencies(buildout, bin_folder):
    """
    Install the flux, overlap, gem and cufflinks binaries.
    """
    # Remove any existing flux in the pipeline bin folder
    buildout_directory = buildout['buildout']['directory']
    dependencies_bin = os.path.join(buildout_directory, 'var/pipeline/bin')
    # Do nothing if the dependencies have been installed already
    if INSTALLATION_STATE.get_reinstall(dependencies_bin):
        return
    install_dependency_flux(buildout, bin_folder)
    install_dependency_overlap(buildout, bin_folder)
    install_dependency_gem(buildout, bin_folder)
    install_dependency_nextgem(buildout, bin_folder)
    install_dependency_cufflinks(buildout, bin_folder)
    install_dependency_fastqc(buildout, bin_folder)
    # Mark dependencies as installed
    INSTALLATION_STATE.set_reinstall(dependencies_bin)


def install_dependency_flux(buildout, bin_folder):
    """Make symbolic links to the Flux"""
    buildout_directory = buildout['buildout']['directory']
    target = os.path.join(bin_folder, 'flux')
    if os.path.exists(target):
        os.remove(target)
    if os.path.exists(target):
        raise AttributeError
    buildout_directory = buildout['buildout']['directory']
    # The flux gets install inside the var/pipeline/bin folder
    pipeline_bin = os.path.join(buildout_directory, 'src/flux/bin')
    os.symlink(os.path.join(pipeline_bin, 'flux'), target)
    if not os.path.exists(target):
        raise AttributeError("Flux shell script not found", target)


def install_dependency_overlap(buildout, bin_folder):
    """Make symbolic links to overlap"""
    target = os.path.join(bin_folder, 'overlap')
    os.symlink(buildout['settings']['overlap'], target)
    if not os.path.exists(target):
        raise AttributeError("Overlap binary not found: %s" % target)


def install_dependency_gem(buildout, bin_folder):
    """Make symbolic links to the gem binaries"""
    gem_binary_glob = os.path.join(buildout['settings']['gem_folder'], 'gem-*')
    for source in glob.glob(gem_binary_glob):
        gem_binary = os.path.split(source)[-1]
        target = os.path.join(bin_folder, gem_binary)
        os.symlink(source, target)
        if not os.path.exists(target):
            raise AttributeError("Gem binary not found: %s" % target)


def install_dependency_nextgem(buildout, bin_folder):
    """Make symbolic links to the nextgem binaries"""
    folder = buildout['settings']['nextgem_folder']
    nextgem_binary_glob = os.path.join(folder, 'gem-*')
    for source in glob.glob(nextgem_binary_glob):
        if source.endswith('.man'):
            continue
        nextgem_binary = os.path.split(source)[-1]
        target = os.path.join(bin_folder, 'next%s' % nextgem_binary)
        os.symlink(source, target)
        if not os.path.exists(target):
            raise AttributeError("Gem binary not found: %s" % target)


def install_dependency_cufflinks(buildout, bin_folder):
    """Make symbolic links to Cufflinks"""
    buildout_directory = buildout['buildout']['directory']
    cufflinks_folder = os.path.join(buildout_directory, 'src/cufflinks')
    for cufflinks_binary in CUFFLINKS_BINARIES:
        source = os.path.join(cufflinks_folder, cufflinks_binary)
        target = os.path.join(bin_folder, cufflinks_binary)
        os.symlink(source, target)
        if not os.path.exists(target):
            raise AttributeError("Cufflinks binary not found: %s" % target)


def install_dependency_fastqc(buildout, bin_folder):
    """Make symbolic links to Fastqc"""
    buildout_directory = buildout['buildout']['directory']
    fastqc_folder = os.path.join(buildout_directory, 'src/fastqc')
    fastqc_binary = 'fastqc'
    source = os.path.join(fastqc_folder, fastqc_binary)
    os.chmod(source, 0755)
    target = os.path.join(bin_folder, fastqc_binary)
    os.symlink(source, target)
    if not os.path.exists(target):
        raise AttributeError(target)
    patch_perl_script(buildout, target)
    if not os.path.exists(target):
        raise AttributeError("Fastqc binary not found: %s" % target)


def parse_read_length(accession):
    """
    Given a readType, parse the read length

    readType can be for example:

    2x50, 75D, 2x76D, 1x70D, 2x75, 1x80, 1x40, 1x75D, 2x100
    2x96, 2x53, 2x76, 2x46, 2x35, 2x34, 100, 2x40, 2x50, 2x51
    2x54, 2x49, 2x36, 1x36, 2x37, 50, 75
    """
    read_length = accession['readType']
    if 'D' in read_length:
        read_length = read_length.split('D')[0]
    if 'x' in read_length:
        # Extract the read length taking the value after the x
        read_length = read_length.split('x')[1]
    if read_length.isdigit():
        return read_length
    else:
        return None


def parse_trim_length(pipeline):
    """
    Given a trim length, make sure it is an integer.
    """
    trim_length = pipeline.get('MIN_RECURSIVE_MAPPING_TRIM_LENGTH', '')
    if trim_length.isdigit():
        return trim_length
    else:
        return None


def parse_flux_mem(pipeline):
    """
    Given a flux mem parameter, make sure it is an integer.
    If it ends with G (G for giga bytes), accept the integer before,
    and strip the G.
    """
    flux_mem = pipeline.get('FLUXMEM', '')
    if flux_mem.endswith('G'):
        flux_mem = flux_mem[:-1]
    if flux_mem.isdigit():
        return flux_mem
    else:
        return None


def get_pipeline_script_command(accession, pipeline, options):
    """
    Assemble the command line options for the start and clean scripts.
    """
    command = "#!/bin/bash\n"
    command += "bin/start_RNAseq_pipeline.3.0.pl"
    command += " -species '%s'" % accession['species']
    command += " -genome %s" % pipeline['GENOMESEQ']
    command += " -annotation %s" % pipeline['ANNOTATION']
    command += " -project %s" % pipeline['PROJECTID']
    command += " -experiment %s" % options['experiment_id']
    command += " -template %s" % pipeline['TEMPLATE']
    read_length = parse_read_length(accession)
    if not read_length is None:
        command += " -readlength %s" % read_length
    command += " -cellline '%s'" % accession['cell']
    command += " -rnafrac %s" % accession['rnaExtract']
    command += " -compartment %s" % accession['localization']
    if 'replicate' in accession:
        command += " -bioreplicate %s" % accession['replicate']
    command += " -threads %s" % pipeline['THREADS']
    command += " -qualities %s" % accession['qualities']
    if 'CLUSTER' in pipeline:
        if str(pipeline['CLUSTER']).strip() == '':
            raise AttributeError("CLUSTER has not been specified")
        else:
            command += " -cluster %s" % pipeline['CLUSTER']
    command += " -database %s" % pipeline['DB']
    command += " -commondb %s" % pipeline['COMMONDB']
    if 'HOST' in pipeline:
        command += " -host %s" % pipeline['HOST']
    command += " -mapper %s" % pipeline['MAPPER']
    command += " -mismatches %s" % pipeline['MISMATCHES']
    if 'MAXINTRONLENGTH' in pipeline:
        command += " -maxintronlength %s" % pipeline['MAXINTRONLENGTH']
    if 'description' in options:
        command += " -run_description '%s'" % options['description']
    if 'PREPROCESS' in pipeline:
        command += " -preprocess '%s'" % pipeline['PREPROCESS']
    if 'PREPROCESS_TRIM_LENGTH' in pipeline:
        template = " -preprocess_trim_length %s"
        command += template % pipeline['PREPROCESS_TRIM_LENGTH']
    trim_length = parse_trim_length(pipeline)
    if not trim_length is None:
        command += " -trimlength %s" % trim_length
    flux_mem = parse_flux_mem(pipeline)
    if not flux_mem is None:
        command += " -fluxmem %sG" % flux_mem
    return command


def install_pipeline_scripts(options, buildout, accession):
    """
    Install the start, execute and clean shell scripts
    """

    # The default pipeline section is called "pipeline"
    pipeline = {}
    if 'pipeline' in buildout:
        pipeline = buildout['pipeline'].copy()

    # If the accession has a pipeline attribute, this overrides the defaults
    # of the pipeline section
    if 'pipeline' in options:
        if options['pipeline'] in buildout:
            pipeline.update(buildout[options['pipeline']].copy())
        else:
            # The advertised pipeline configuration is not there
            raise AttributeError

    command = get_pipeline_script_command(accession, pipeline, options)

    target = os.path.join(options['location'], 'start.sh')
    start_file = open(target, 'w')
    start_file.write(command)
    start_file.close()
    os.chmod(target, 0755)

    target = os.path.join(options['location'], 'clean.sh')
    command += " -clean"
    clean_file = open(target, 'w')
    clean_file.write(command)
    clean_file.close()
    os.chmod(target, 0755)

    command = "#!/bin/bash\n"
    command += "bin/execute_RNAseq_pipeline3.0.pl all |tee -a pipeline.log"
    target = os.path.join(options['location'], 'execute.sh')
    execute_file = open(target, 'w')
    execute_file.write(command)
    execute_file.close()
    os.chmod(target, 0755)


def quick(options, buildout):
    """
    This is the recipe for running the pipeline quickly without specifying
    any meta data, for a given species.
    """
    options = {'accession': 'Run',
               'location': options['location'],
               }
    fastqs = quick_fastqs()
    gtfs = quick_gtf()
    fas = quick_fa()
    species = quick_species(gtfs, fas)
    if species is None:
        template = "Genome and annotation files don't match: %s %s"
        raise AttributeError(template % (gtfs, fas))

    buildout_directory = buildout['buildout']['directory']

    accession = {'file_location': '\n'.join(fastqs),
                 'species': species,
                 'readType': '76',
                 'cell': 'Unknown',
                 'rnaExtract': 'Unknown',
                 'localization': 'Unknown',
                 'qualities': 'phred',
                 'pair_id': '\n'.join([str(i) for i in range(len(fastqs))]),
                 'mate_id': '\n'.join([str(i) for i in range(len(fastqs))]),
                 'label': '\n'.join(['Run' for i in range(len(fastqs))]),
                 'paired': '0',
                 'accession': 'Run'
                 }

    template = os.path.join(buildout_directory, 'src/pipeline/template3.0.txt')

    pipeline = {'GENOMESEQ': gtfs[0],
                'ANNOTATION': fas[0],
                'PROJECTID': 'Quick',
                'TEMPLATE': template,
                'THREADS': 1,
                'DB': 'Quick_RNAseqPipeline',
                'COMMONDB': 'Quick_RNAseqPipelineCommon',
                'MAPPER': 'GEM',
                'MISMATCHES': '2',
                }
    buildout = {'Run': accession,
                'buildout': {'directory': buildout_directory},
                'settings': buildout['settings'].copy(),
                'pipeline': pipeline
                }
    main(options, buildout)


def quick_fastqs():
    """Return list of .fastq files found"""
    filenames = glob.glob("*.fastq.gz")
    cwd = os.getcwd()
    fastqs = []
    for filename in filenames:
        fastqs.append(os.path.join(cwd, filename))
    if len(fastqs) == 0:
        raise AttributeError("Please drop *.fastq.gz files into this folder")
    return fastqs


def quick_gtf():
    """Return list of .gtf files found"""
    filenames = glob.glob("*.gtf")
    cwd = os.getcwd()
    gtfs = []
    for filename in filenames:
        gtfs.append(os.path.join(cwd, filename))
    if len(gtfs) != 1:
        template = "Please provide just one genome file. Found: %s"
        raise AttributeError(template % gtfs)
    return gtfs


def quick_fa():
    """Return list of .fa files found"""
    fas = glob.glob("*.fa")
    cwd = os.getcwd()
    filenames = []
    for filename in filenames:
        fas.append(os.path.join(cwd, filename))
    if len(fas) != 1:
        template = "Please provide just one annotation file. Found: %s"
        raise AttributeError(template % fas)
    return fas


def quick_species(gtfs, fas):
    """Deduct species from given gtf and fas files"""
    text = str(gtfs) + str(fas)
    species = None
    if "gencode.v7.annotation.ok.gtf" in text:
        if "H.sapiens.genome.hg19.main.fa" in text:
            species = "Homo sapiens"
    elif "mm9_ucsc_UCSC_genes.gtf" in text:
        if "M.musculus.genome.mm9.main.fa" in text:
            species = "Mus musculus"
    elif "flyBase.exons.genes_real.transcripts.gtf" in text:
        if "D.melanogaster.genome.fa" in text:
            species = "Drosophila Melanogaster"
    return species


def main(options, buildout):
    """
    This method is called for each part and does the following:

    * Create a fresh readData folder with pointers to the original read files

    * bin folder

        * The /src/pipeline/bin folder is copied to var/pipeline/bin

        * The shebangs of all Perl scripts in var/pipeline/bin is changed to
          use the Perl version defined in buildout.cfg

        * Create a fresh link in the part to the var/pipeline/bin folder

    * lib folder

        * The /src/pipeline/lib folder is copied to var/pipeline/lib

        * Create a fresh link in the part to the var/pipeline/lib folder
    """
    # Without an accession, the part can not be created, because no read files
    # can be linked to
    try:
        accession = buildout[options['accession']]
    except KeyError:
        if buildout['runs']['parts'] in ['Run']:
            quick(options, buildout)
            return
        print "Accession not found", options['accession']
        return

    for key, value in accession.items():
        if not key in ['pair_id',
                       'mate_id',
                       'label',
                       'file_location',
                       'file_type']:
            if '\n' in value:
                # Collapse the redundant values to make labeling easier
                accession[key] = value.split('\n')[0]

    # The part name is also the experiment id. As it is not given in the
    # options, we need to extract it from the current location. Sigh.
    options['experiment_id'] = os.path.split(options['location'])[-1]

    buildout_directory = buildout['buildout']['directory']

    bin_folder = os.path.join(buildout_directory, 'var/pipeline/bin')
    install_bin_folder(options, buildout, bin_folder)

    # The lib folder is copied to var/pipeline
    lib_folder = os.path.join(buildout_directory, 'var/pipeline/lib')
    install_lib_folder(options, buildout, lib_folder)

    experiment_id = options['experiment_id']
    results_folder = os.path.join(buildout_directory, 'var/%s' % experiment_id)
    install_results_folder(options, results_folder)

    gemindices_folder = os.path.join(buildout_directory, 'var/GEMIndices')
    install_gemindices_folder(options, gemindices_folder)

    install_read_folder(options, accession)

    if not INSTALLATION_STATE.get_reinstall(bin_folder):
        install_dependencies(buildout, bin_folder)

    install_pipeline_scripts(options, buildout, accession)

    # Check the read labels are consistent with the paired information
    check_read_labels(accession, experiment_id)

    # Install the read list file defining the labels of the reads
    install_read_list(options, accession)

    # As a last step, set the lib and bin folder to the reinstalled state
    INSTALLATION_STATE.set_reinstall(lib_folder)
    INSTALLATION_STATE.set_reinstall(bin_folder)
