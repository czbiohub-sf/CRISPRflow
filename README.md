# CRISPRflow
### MAGeCK analysis automated by Nextflow
### modified based on https://github.com/FredHutch/crispr-screen-nf

## Dependencies
- [Docker](https://docs.docker.com/get-docker/)
- [Java 11 (or later, up to 17)](https://www.oracle.com/java/technologies/downloads/)

## Usage: 
clone the repository
```
git clone https://github.com/czbiohub/CRISPRflow.git
```
Go the repository directory, switch he branch if running branch other than master
```
cd CRISPRflow
git checkout <branch you'd like to run>
```
Create conda environment and activated it
```
conda env create -f environment.yml
conda activate CRISPRflow
```
Pull docker images
```
cd helper_scripts
bash pull_docker_imgs.sh
```
Check fastq files and create nextflow commands
```
#in directory helper_scripts
python check_files_and_get_nf_cmds.py --csv example_LibA.csv
```
Start nextflow
```
cd .. # in directory CRISPRflow
bash example_LibA.csv.sh
```
