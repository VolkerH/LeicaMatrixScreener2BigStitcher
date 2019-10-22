# CAUTION - WORK IN PROGRESS ... 

# LM2BS Convert Leica Matrix Screener acquistion to Big Stitcher projects

![workflow_overview](./illustrations/workflow_overview.JPG)

## About

`lm2bs_gui` is a Python app that allows converting microscopy image files acquired with Leica Matrix
Screener to Big Stitcher project, using the meta-data information about the stage position to put each acquired
tile in the correct initial position. 

The folder `fiji_batch_scripting` contains some ImageJ/Fiji Jython scripts that perform batch stitching, fusion and export of the generated Big Stitcher projects.

In addition, this repo has some brief notes on how to set up a matrix screener tile scan and how to perform smart acquitision using the Leica CAM interface. 

## Installation & Start

Create a python environment using `conda` and install dependencies (only needed once.)

* Install anaconda/miniconda
* Start a terminal or cmd window
* Create a new conda environment `conda env create -n lm2bs python=3.6`
* Activate the environment `conda activate lm2bs`
* `conda install -c conda-forge scikit-image pandas tifffile tifffolder pyqt h5py`

Startup

* activate the conde environment `conda activate lm2bs`
* in the `lm2bs`  folder execute `python lm2bs_gui.py`

## Setting up a matrix screener scan


## Usage:

### Matrix screener output 

The output from matrix screener is a nested folder structure with levels such  `experiment-*`, `slide-*`, `chamber-*` and `field-*`.
When using the Matrix Screener in the mode multiple subpositions in multiple wells, `chamber`-folders refer
to individual wells and `field-` folders refer to individual subpositions in those wells. Each field folder
contains the captured images in `.ome.tif` format with one tif file per channel and z-slice.

### Select 

### Stitching in Big Stitcher


### Batch Stitching

The folder [./fiji_batch_stitching] contains Fiji scripts that can automate the stitching fusion and 
export for several subfolders.

## Limitations / TODO

* currently only a single channel is supported. Extending this to multiple channels should be straightforward, but I do not have a dataset to test this on
* the code currently assumes that each `field--*` folder only contains images from a single scan job (this can be identified by the `--J` part of the file name). If there is a mixture of different scan jobs (e.g. files with `--J08` and `--J09`) I suspect there will be issues with reading the stacks. This can occur for example if a software autofocus routine is run (for some versions of Matrix Screener the autofocus images are saved in the same folder). The fix in the code (filtering file names based on job number) should be straightforward.

## Acknowledgements

* The sample dataset of drosophila ovarioles was captured in collaboration with André Nogueira Alves from the [the Mirth lab at Monash University](http://themirthlab.org/) who did the sample preparation. One of the stitched sample volumes is availabe under a [CC-BY license on figshare](https://figshare.com/articles/_/9985568).
* This tool leverages prior efforts by Talley Lambert and Nikita Valdimirov, namely [npy2bdv (bundled)](https://github.com/nvladimus/npy2bdv) and [tifffolder](https://github.com/tlambert03/tifffolder).
* [Big Stitcher from the Preibisch Lab](https://www.nature.com/articles/s41592-019-0501-0)