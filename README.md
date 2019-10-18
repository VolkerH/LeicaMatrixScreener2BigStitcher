# CAUTION - WORK IN PROGRESS ... 

# LM2BS Convert Leica Matrix Screener acquistion to Big Stitcher projects

##  About

`lm2bs_gui` is a Python app that allows converting microscopy image files acquired with Leica Matrix
Screener to Big Stitcher project, using the meta-data information about the stage position to put each acquired
tile in the correct initial position. 

The folder `fiji_batch_scripting` contains some ImageJ/Fiji Jython scripts that perform batch stitching, fusion and export of the generated Big Stitcher projects.

In addition, this repo has some brief notes on how to set up a matrix screener tile scan and how to perform smart acquitision using the Leica CAM interface. 

## Installation

* Install anaconda/miniconda
* Create a new conda environment `conda env create -n lm2bs`
* 