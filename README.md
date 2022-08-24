# CRISPRflow
### MAGeCK analysis automated by Nextflow
### modified based on https://github.com/FredHutch/crispr-screen-nf

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
More to be added
