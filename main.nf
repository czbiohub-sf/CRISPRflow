#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// Set default parameters
params.help = false
params.fastq = false
params.library = false
params.ntc_list = false
params.output = false
params.output_prefix = false
params.mle_designmat = false
params.organism = 'hsa'
params.scale_cutoff = 1
params.skip_flute = false
params.treatname = false
params.ctrlname = false
params.merge_sublibrary = false

// Space delimited list of file endings to be removed from
// FASTQ file names to yield the samples names that they
// correspond to
params.suffix_list = "gz fq fastq fna fasta"

// Import the modules
include {
    mageck as mageck_A;
    mageck as mageck_B;
    mageck as mageck_noSublib;
    concat_sublib_counts as concat_sublib_counts_treatment;
    concat_sublib_counts as concat_sublib_counts_control;
    join_counts as join_counts_A;
    join_counts as join_counts_B;
    join_counts as join_counts_ALL;
    mageck_test_rra;
    mageck_test_ntc;
    mageck_test_mle;
    mageck_flute_rra;
    mageck_flute_mle;
} from './modules' params(
    suffix_list: params.suffix_list,
    output: params.output,
    output_prefix: params.output_prefix,
    organism: params.organism,
    scale_cutoff: params.scale_cutoff,
    treatname: params.treatname,
    ctrlname: params.ctrlname
)

// Function which prints help message text
def helpMessage() {
    log.info
    """
    Usage:
    nextflow run FredHutch/crispr-screen-nf

    Required Arguments:
        --treatment_fastq   Path to FASTQ data for treatment samples
        --control_fastq     Path to FASTQ data for control samples
                            Multiple files can be specified with wildcards and commas, e.g.
                                /path/to/inputs/A/*.fastq.gz,/path/to/inputs/B/*.fq.gz
        --library           Text file describing sgRNA library
                                As described at https://sourceforge.net/p/mageck/wiki/input/
        --output            Path to output directory
        --output_prefix     Prefix for all output files

    Optional Arguments:
        --ntc_list          Path to file describing negative controls
                                As described in https://sourceforge.net/p/mageck/wiki/input/#negative-control-sgrna-list
        --mle_designmat     To use MAGeCK-mle to call gene essentiality, use this flag
                                to specify the path a design matrix file as described in
                                https://sourceforge.net/p/mageck/wiki/demo/#the-fourth-tutorial-using-mageck-mle-module
        --organism          Organism string provided for MAGeCK-Flute (default: hsa)
        --scale_cuttoff     Parameter 'scale_cutoff' for MAGeCK-Flute (default: 1)
        --skip_flute        MAGeCK-Flute is only compatible with human (hsa) or mouse (mmu) gene symbols.
                            If the guide library contains gene symbols which are not compatible, set this
                            flag to skip the MAGeCK-Flute portion of the analysis.
        --treatname         Name of treatment group from design matrix (required for FluteMLE)
        --ctrlname          Name of control group from design matrix (required for FluteMLE)
    """
    }

workflow {

    main:
        
    // If the user used the --help flag
    if(params.help){

        // Display the help text
        helpMessage()

        // And exit with an error code
        exit 1
    }

    // If the user did not specify a FASTQ input path for treatment samples
    if(!params.treatment_fastq){

        // Inform them of the error
        log.info"""

        ERROR: The --treatment_fastq flag must be provided to specify input files for treatment samples
        Use the --help flag for more details

        """
        // And exit with an error code
        exit 1
    }

    // If the user did not specify a FASTQ input path for control samples
    if(!params.control_fastq){

        // Inform them of the error
        log.info"""

        ERROR: The --control_fastq flag must be provided to specify input files for control samples
        Use the --help flag for more details

        """
        // And exit with an error code
        exit 1
    }

    // If the user did not specify a library input path
    if(!params.library){

        // Inform them of the error
        log.info"""

        ERROR: The --library flag must be provided to specify input files
        Use the --help flag for more details

        """
        // And exit with an error code
        exit 1
    }

    // If the user did not specify an output path
    if(!params.output){
        // Inform them of the error
        log.info"""

        ERROR: The --output flag must be provided to specify an output directory
        Use the --help flag for more details
        
        """
        // And exit with an error code
        exit 1
    }

    // Read the sgRNA library file
    Channel
        .fromPath(params.library.split(",").toList())
        .branch{
           sublib_A: it =~ /.*_A_.*/
           sublib_B: it =~ /.*_B_.*/
           all: true
        }
        .set{sgrna_library}
    

    // Make a channel with the input reads for treatment samples
    Channel
        .fromPath(params.treatment_fastq.split(",").toList())
        .branch{
           sublib_A: it =~ /.*_A_.*/
           sublib_B: it =~ /.*_B_.*/
           all: true
        }
        .set{treatment_reads_ch}
        
    //treatment_reads_ch.sublib_A.view{ "$it uses sublib A"}
    //treatment_reads_ch.sublib_B.view{ "$it uses sublib B"}

    // Make a channel with the input reads for control samples
    Channel
        .fromPath(params.control_fastq.split(",").toList())
        .branch{
           sublib_A: it =~ /.*_A_.*/
           sublib_B: it =~ /.*_B_.*/
           all: true

        }
        .set{control_reads_ch}

    // Make channels to signal the completion of counts
    Channel
        .of()
        .branch{
           sublib_A: it =~ /.*_A_.*/
           sublib_B: it =~ /.*_B_.*/
           all: true
        }
        .set{count_done_ch}

    //treatment_reads_ch.all.ifEmpty("use_sublibrary")
    treatment_reads_ch.sublib_A.view()
    treatment_reads_ch.sublib_B.view()
    treatment_reads_ch.all.view()

    control_reads_ch.sublib_A.view()
    control_reads_ch.sublib_B.view()
    control_reads_ch.all.view()

    sgrna_library.sublib_A.view()
    sgrna_library.sublib_B.view()
    sgrna_library.all.view()

    library_A_flag = (params.treatment_fastq ==~ /.*_A_.*/ & params.control_fastq ==~ /.*_A_.*/ & params.library ==~ /.*_A_.*/)
    library_B_flag = (params.treatment_fastq ==~ /.*_B_.*/ & params.control_fastq ==~ /.*_B_.*/ & params.library ==~ /.*_B_.*/)

    if (!library_A_flag && library_B_flag)
    {

        log.info"""

        ERROR: Library A file(s) missing (treat and control fastq, sgRNA library)
        
        """
        // And exit with an error code
        exit 1
    }

    if (library_A_flag && !library_B_flag)
    {
        log.info"""

        WARNING: Library B file(s) missing, proceding as no Sublibrary
        
        """
    }
    
    if (library_A_flag && library_B_flag)
    {
        //concat sublib counts and run test_rra
        mageck_A(treatment_reads_ch.sublib_A.toSortedList(), control_reads_ch.sublib_A.toSortedList(), sgrna_library.sublib_A, "Lib_A")
        mageck_B(treatment_reads_ch.sublib_B.toSortedList(), control_reads_ch.sublib_B.toSortedList(), sgrna_library.sublib_B, "Lib_B")
        concat_sublib_counts_treatment(mageck_A.out.counts.toSortedList(),mageck_B.out.counts.toSortedList())
        mageck_test_rra(concat_sublib_counts_treatment.out.concat.toSortedList())
    }
    else
    {
        //not using sublirary, no bio reps
        //count
        mageck_noSublib(treatment_reads_ch.all.toSortedList(), control_reads_ch.all.toSortedList(), sgrna_library.all, "all")
        //run test_rra
        mageck_test_rra(mageck_noSublib.out.counts.toSortedList())
    }





    // )

    // treatment_mageck_A.out.subscribe onComplete: {
    //     control_mageck_A.out.subscribe onComplete: {
    //         println "Count completed for library A treatment + control"


    //     }
    // }

    // if (library_A_flag == 1 & library_B_flag == 1)
    // {
    //     //merge sublib
    //     concat_sublib_counts_treatment(
    //         treatment_mageck_A.out.collect()
    //         treatment_mageck_B.out.collect()
    //     )

        //merge control
        // concat_sublib_counts_control(
        //     control_mageck_A.out.collect()
        //     control_mageck_B.out.collect()
        // )
    //}





    // if ((library_A_flag + library_B_flag) ==2)
    // {
    //     // Join together the counts from all samples for sub-library A
    //     concat_sublib_counts_A(
    //         treatment_mageck_A.out.toSortedList(),
    //         control_mageck_A.out.toSortedList(),
    //     )
    //     // Join together the counts from all samples for sub-library B            
    //     concat_sublib_counts_B(
    //         treatment_mageck_B.out.toSortedList(),
    //         control_mageck_B.out.toSortedList(),
    //     )
    // }







        // Join together the counts from all samples for sub-library A
        //join_counts(
        //    treatment_mageck.out.toSortedList(),
        //    control_mageck.out.toSortedList(),
        //)

        // Join together the counts from all samples for sub-library B
        //join_counts2(
        //    treatment_mageck.out.toSortedList(),
        //    control_mageck.out.toSortedList(),
        //)

        // Concatenate sublibraries 
        //concat_sublib_counts(
        //    join_counts.out,
        //    join_counts2.out,
        //)



        // Join together the counts from all samples
        //join_counts(
        //    treatment_mageck.out.toSortedList(),
        //    control_mageck.out.toSortedList(),
        //)
    
        

}