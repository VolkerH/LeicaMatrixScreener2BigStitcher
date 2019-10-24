#@ File(label="Select a folder", style="directory") basefolder


# Script to automatically stitch and fuse all datasets in a folder
# checks all subfolders below the selected folder to determine whether they contain a dataset.xml
# Pairwise shift and fusion parameters are hardcoded. Adjust below or add to op parameters.

from ij import IJ as IJ
import os


def process_folder(foldername, dataset="dataset.xml"):
	xmlname = foldername+"/"+dataset
	IJ.run("Calculate pairwise shifts ...", "select=" + xmlname + " process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints]");
	IJ.run("Fuse dataset ...", "select=" + xmlname + " process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[All Views] downsampling=11 pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation] image=[Precompute Image] interest_points_for_non_rigid=[-= Disable Non-Rigid =-] blend preserve_original produce=[All views together] fused_image=[Save as (compressed) TIFF stacks] output_file_directory=" + foldername + " lossless");

def has_bigstitcher_dataset(pathname):
	if os.path.isdir(pathname):
		if os.path.exists(pathname+os.path.sep+"dataset.xml"):
			return True
	return False

base = str(basefolder)
files = os.listdir(base)
files = [ base+"/"+f for f in files]

big_stitcher_folders= filter(has_bigstitcher_dataset, files)
print(big_stitcher_folders)

for folder in big_stitcher_folders:
	print("Processing Folder "+folder)
	process_folder(folder)