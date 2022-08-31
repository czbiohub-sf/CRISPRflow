# CRISPRflow
### MAGeCK analysis automated by Nextflow
### modified based on https://github.com/FredHutch/crispr-screen-nf

## Dependencies
- [Docker](https://docs.docker.com/get-docker/)
- [Java 11 (or later, up to 17)](https://www.oracle.com/java/technologies/downloads/)
- [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Usage: 
clone the repository
```
git clone https://github.com/czbiohub/CRISPRflow.git
```
Go the repository directory, switch the branch if running branch other than master
```
cd CRISPRflow
git checkout <branch you'd like to run>
```
Create conda environment and activate it
```
conda env create -f environment.yml
conda activate CRISPRflow
```
Pull docker images
```
bash helper_scripts/pull_docker_imgs.sh 
```
Check fastq files and create nextflow commands
```
python helper_scripts/check_files_and_get_nf_cmds.py --csv metadata/example_LibA.csv #example 1
python helper_scripts/check_files_and_get_nf_cmds.py --csv metadata/example_LibAB.csv #example 2
```
Make the nextflow command executable
```
chmod a+x nextflow
```
Start nextflow
```
bash example_LibA.csv.sh #example 1
bash example_LibAB.csv.sh #example 2
```
## Input
- Fastq files
- A csv file that maps fastq files to each condition/replication/sublibrary  
- A reference library csv file for each (sub)library  

## Fastq files: naming and path
naming and path of fastq files are defined in csv files using the following fields. Each experiment take one row

- Directories
  - **Parent_dir**: the parent folder of Lib_A_dir and Lib_A_dir  
    `example: mydata`  
  - **Lib_A_dir**: the folder containing fastq files from Lib_A or single library experiments  
    `example: Han_influenzaA` 
- File name parts
  - **prefix**: for all fastq file in the same experiment  
    `example: Han_Influenza_`
    - treatment
      - **Lib_A_tr_bio_reps**: Biological replicates  
        `example: LibArep1,LibArep2`  
      - **suffix_tr**: suffix for treatment    
        `example: _Infected.fastq.gz`  
    - control
      - **Lib_A_ctrl_bio_reps**: Biological replicates  
        `example: LibArep1,LibArep2`  
      - **suffix_ctrl**: suffix for conrol    
        `example: _Control.fastq.gz` 
 
The script will check accessbility of the following files:  
`mydata/Han_influenzaA/Han_Influenza_LibArep1_Infected.fastq.gz`   
`mydata/Han_influenzaA/Han_Influenza_LibArep2_Infected.fastq.gz`  
`mydata/Han_influenzaA/Han_Influenza_LibArep1_Control.fastq.gz`    
`mydata/Han_influenzaA/Han_Influenza_LibArep2_Control.fastq.gz`  

For split libraries (A/B), The following columns are needed.
- Lib_B_tr_bio_reps  
- Lib_B_ctrl_bio_reps
- Lib_B_dir  

**Note**: names associated with Library A needs to have "\_A\_" in the naming and Library B need to have "\_B\_"  
For an example, see `metadata/example_LibAB.csv`

## Library reference files
Library reference files should live in the **Lib_A_dir** and **Lib_B_dir**.   
And the file (usually csv files) names should be specificed in the csv file under columns **Lib_A_csv** and **Lib_B_csv**  
For example `GeCKOA_Mageck_ref.csv` `GeCKOB_Mageck_ref.csv`  
For file format, see MAGeCK manual: https://sourceforge.net/p/mageck/wiki/Home/  

## Troubleshooting
Java issues (after installing java):  
For most case, it can be fixed by explicitly specifying the version installed (v17 in the example)
```
unset JAVA_HOME
export JAVA_HOME=`/usr/libexec/java_home -v 17`
```
