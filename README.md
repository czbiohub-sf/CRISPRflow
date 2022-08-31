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

## Troubleshooting
Java issues (after installing java):  
For most case, it can be fixed by explicitly specifying the version installed (v17 in the example)
```
unset JAVA_HOME
export JAVA_HOME=`/usr/libexec/java_home -v 17`
```
