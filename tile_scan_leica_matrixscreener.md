# Leica Matrix Screener

## Matrix Screener Basics

Matrix Screener is an optional add-on available for several versions of the Leica LASAF software.
Among other features, Matrix Screener provides functionality to perform tile scans and to control some 
aspects of the software remotely. (Note that this is separate from the tile scan functionality in the Navigator module.)
 The screenshots here are from 
the LASAF versions that come with the SP5 series of microscopes. The matrix screener GUI for the SP8 Series is organised and styles differently but all the same functionality is there.

[Please refer to this document](https://github.com/VolkerH/MatrixScreenerCellprofiler/wiki
) for an introduction to Matrix Screener, that was written for a slightly different context but explains the basic steps.
 The screenshots there are from 
the LASAF versions that come with the SP5 series of microscopes. The matrix screener GUI for the SP8 Series is organised and styled differently but offers the same functionality.

## Setting up a multi-well tile scan


* Start Matrix Screener, set up auto export paths
* Select the Matrix Screener Application "Multiple Regular Matrices"
* Select the  "Setup Template" register tab at the bottom. Set up the count of wells and count of fields to reflect your sample holder. Set up the well distances according to your well plate and set up the field distances with some overlap to allow for stitching (e.g. 20% smaller than the field of view). You may have to go back to "Setup Template" to this after the following step (setting up the jobs will tell you the field of view.) Navigate the stage to the top-left corner of the top-left well. Under "Start Coordinates" click the "Learn" button to store the current stage position as the origin.
* Select the "Setup Jobs" register tab at the bottom. Set up you scan job (or multiple scan jobs). Take note of the Z-spacing if you are collecting stacks. As you modify the scan settings, the GUI will show you the size of the FOV. You can use this size (minus desired overlap) in the previous step to determine the field spacing.
* Select the "Setup Experiment" register tab at the bottom. Select the fields that you want to image and assign a scan job.
* Press the "Play" button to start the scan.


## Folder/File output struchture and naming for Matrix screener acquisitions

The image data saved during matrix screener acquisitions is a organised in nested folder structure with levels such  `experiment-*`, `slide-*`, `chamber-*` and `field-*`.
When using the Matrix Screener in the mode multiple subpositions in multiple wells, `chamber`-folders refer
to individual wells and `field-` folders refer to individual subpositions in those wells. Each field folder
contains the captured images in `.ome.tif` format with one tif file per channel and z-slice.

[The file `./sample_data/tree.txt` shows the file structure from an example matrix screener experiment](./sample_data/tree.txt).