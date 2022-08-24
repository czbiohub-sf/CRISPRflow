// Container used to run mageck
mageck_container = "quay.io/biocontainers/mageck:0.5.9.4--py38h8c62d01_1"
mageckflute_container = "quay.io/biocontainers/bioconductor-mageckflute:1.12.0--r41hdfd78af_0"

//


// Process used to run MAGeCK count
process mageck {
    container "${mageck_container}"
    label "mem_medium"
    publishDir "${params.output}/${params.output_prefix}/count/", mode: "copy", overwrite: "true", pattern: "*count_normalized.txt"
    publishDir "${params.output}/${params.output_prefix}/count/log", mode: "copy", overwrite: "true", pattern: "*.log" 
    publishDir "${params.output}/${params.output_prefix}/count/countsummary", mode: "copy", overwrite: "true", pattern: "*.countsummary.txt" 
    publishDir "${params.output}/${params.output_prefix}/count/rawcounts", mode: "copy", overwrite: "true", pattern: "*.count.txt" 
    publishDir "${params.output}/${params.output_prefix}/count/r", mode: "copy", overwrite: "true", pattern: "*.Rnw" || "*.Rmd" || "*.R"

    input:
        file 'fastq_tr??.fastq.gz'
        file 'fastq_ctrl??.fastq.gz'
        file(library)
        val(lib)
    output:
        tuple file("*.R"), file("*"), emit: r
        path "*.count_normalized.txt", emit: counts

    script:

        shell:
        '''
        NAMES_tr=$(echo fastq_tr*.fastq.gz | sed "s/ /,/g")
        NAMES_ctrl=$(echo fastq_ctrl*.fastq.gz | sed "s/ /,/g")

        echo FASTQ file is fastq_tr*.fastq.gz fastq_ctrl*.fastq.gz
        echo Sample name is ${NAMES_tr},${NAMES_ctrl}

        mageck count -l !{library} -n !{params.output_prefix}!{lib} --sample-label ${NAMES_tr},${NAMES_ctrl} --fastq fastq_tr??.fastq.gz fastq_ctrl??.fastq.gz --norm-method total
        '''

}

//concat counts for each sublib
process concat_sublib_counts{
    container "${mageck_container}"
    label "io_limited"
    publishDir "${params.output}/${params.output_prefix}/count/", mode: "copy", overwrite: "true"

    input:
        file(A_count_normalized) 
        file(B_count_normalized) 
    
    output:
        path "*", emit: concat
    script:
        """/bin/bash

        set -Eeuo pipefail

        #remove header from "A" count file (we want to modify the header)
        tail -n+2 ${A_count_normalized} > ${A_count_normalized}_noheader

        #remove header row from "B" count file:
        tail -n+2 ${B_count_normalized} > ${B_count_normalized}_noheader

        #Concatemerize A file and B file without header
        head -n1 ${A_count_normalized} | cat - ${A_count_normalized}_noheader ${B_count_normalized}_noheader > ${params.output_prefix}AB_count_normalized.txt

        #remove temporary files
        rm ${A_count_normalized}_noheader
        rm ${B_count_normalized}_noheader
        """
}

// Process used to run MAGeCK test
process mageck_test_rra {
    container "${mageck_container}"
    label "io_limited"
    publishDir "${params.output}/${params.output_prefix}/rra/", mode: "copy", overwrite: "true"

    input:
        file(counts_tsv)

    output:
        file "${params.output_prefix}.*"

    script:
        shell:
        """

        set -Eeuo pipefail

        num_tr=\$(head -n 1 !{counts_tsv} | grep -o "fastq_tr" | wc -l)
        num_ctrl=\$(head -n 1 !{counts_tsv} | grep -o "fastq_ctrl" | wc -l)

        t_seq=\$(seq -s, 0 1 \$(expr \$num_tr - 1))
        c_seq=\$(seq -s, \$num_tr 1 \$(expr \$num_tr + \$num_ctrl - 1))

        echo \$num_tr
        echo \$num_ctrl        
        echo \$t_seq
        echo \$c_seq

        mageck test \
            -k !{counts_tsv} \
            -t \$t_seq \
            -c \$c_seq \
            -n "!{params.output_prefix}" \
            --norm-method none \
            --sort-criteria pos

        ls -lahtr
        """
}


// Process used to run MAGeCK test with the --control-sgrna option
process mageck_test_ntc {
    container "${mageck_container}"
    label "io_limited"
    publishDir "${params.output}/rra/", mode: "copy", overwrite: "true"

    input:
        tuple file(counts_tsv), file(treatment_samples), file(control_samples), file(ntc_list)

    output:
        file "${params.output_prefix}.*"

    script:
"""/bin/bash

set -Eeuo pipefail

mageck test \
    -k ${counts_tsv} \
    -t "\$(cat ${treatment_samples})" \
    -c "\$(cat ${control_samples})" \
    -n "${params.output_prefix}" \
    --control-sgrna ${ntc_list} \
    --norm-method total

ls -lahtr
"""

}

// Process used to run MAGeCK-mle test with the --mle_designmat option
process mageck_test_mle {
    container "${mageck_container}"
    label "io_limited"
    publishDir "${params.output}/mle/", mode: "copy", overwrite: "true"

    input:
        tuple file(counts_tsv), file(treatment_samples), file(control_samples), file(designmat)

    output:
        file "${params.output_prefix}.*"

    script:
"""/bin/bash

set -Eeuo pipefail

mageck mle \
    -k ${counts_tsv} \
    -d ${designmat} \
    -n "${params.output_prefix}"

ls -lahtr
"""

}

// Process used to run MAGeCK FluteRRA
process mageck_flute_rra {
    container "${mageckflute_container}"
    label "io_limited"
    publishDir "${params.output}/rra_flute/", mode: "copy", overwrite: "true"

    input:
        file "*"

    output:
        file "MAGeCKFlute_${params.output_prefix}/*"

    script:
"""/bin/bash

set -Eeuo pipefail

mageck_flute_rra.R \
    "${params.output_prefix}.gene_summary.txt" \
    "${params.output_prefix}.sgrna_summary.txt" \
    "${params.output_prefix}" \
    "${params.organism}" \
    "${params.scale_cutoff}"
    
"""

}

// Process used to run MAGeCK FluteMLE
process mageck_flute_mle {
    container "${mageckflute_container}"
    label "io_limited"
    publishDir "${params.output}/mle_flute/", mode: "copy", overwrite: "true"

    input:
        file "*"

    output:
        file "MAGeCKFlute_${params.output_prefix}/*"

    script:
"""/bin/bash

set -Eeuo pipefail

mageck_flute_mle.R \
    "${params.output_prefix}.gene_summary.txt" \
    "${params.output_prefix}" \
    "${params.organism}" \
    "${params.treatname}" \
    "${params.ctrlname}"
    
"""

}

// Process used to join the outputs from mageck / counts
process join_counts {
    container "quay.io/fhcrc-microbiome/python-pandas:v1.2.1_latest"
    label "io_limited"

    input:
        file "treatment/treatment_*.txt"
        file "control/control_*.txt"

    output:
        tuple file("${params.output_prefix}.count_normalized.txt"), file("treatment_sample_names.txt"), file("control_sample_names.txt")

    script:
"""
set -Eeuo pipefail

join_counts.py "${params.output_prefix}"

"""
}


