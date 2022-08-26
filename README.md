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
bash helper_scripts/pull_docker_imgs.sh
```
Check fastq files and create nextflow commands
```
python helper_scripts/check_files_and_get_nf_cmds.py --csv metadata/example_LibA.csv
```
Make the nextflow command excutable
```
chmod a+x nextflow
```
Start nextflow
```
bash example_LibA.csv.sh
```
