#!/bin/csh
### SLURM batch script

### Email address
#SBATCH --mail-user=jmm0111@uah.edu

### TOTAL processors (number of tasks)
#SBATCH --ntasks 64

### total run time estimate (D-HH:MM)
#SBATCH -t 0-01:00

#SBATCH --mem=3G

### Mail to user on job done and fail
#SBATCH --mail-type=END,FAIL

### Partition (queue), select shared for GPU
### Optionally specify a GPU type: --gres=gpu:rtx5000:1 or --gres=gpu:a100:1
### Three hashtags mean that the line is a comment. Uncomment the sbatch line you want
### You can leave the --gres= part blank to let the system select a gpu or comment out all sbatch lines to use shared nodes.
###SBATCH -p shared --gres=gpu:a100:1
###SBATCH -p shared --gres=gpu:rtx5000:1
#SBATCH -p standard

### Job name
#SBATCH -J typical_image_percentage

###Don't overwrite existing out and error files
###SBATCH --open-mode=append

### Paths to information files
#SBATCH -o typical_image_percentage.out ## STDOUT
#SBATCH -e typical_image_percentage.err ## STDERR

module load cuda

### Set dynamic link loader path variable to include CUDA and bins from mamba- change to your paths
setenv LD_LIBRARY_PATH /common/pkgs/cuda/cuda-11.4/lib64
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/common/pkgs/cuda/cuda-11.4/extras/CUPTI/lib64
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/rhome/jmayhall/miniforge3/envs/CNN/lib


### Change the below line to where your code directory is
cd /rstor/jmayhall/

###Change the below line to where python environment (either miniforge or anaconda) is
set runcmd = /rhome/jmayhall/miniforge3/envs/CNN/bin/python

### Chnage the below line to your python file name
${runcmd} -u typical_image_percentage.py