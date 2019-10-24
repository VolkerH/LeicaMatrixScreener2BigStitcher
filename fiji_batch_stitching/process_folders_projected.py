#@ File(label="Select a folder", style="directory") basefolder
#@ Integer(label="downsampling factor fused image", required=true, value=1, stepSize=1) downsample

#
# Script to automatically stitch and fuse all datasets in Batch folder

from ij import IJ as IJ
import os


def process_folder(foldername, dataset="dataset.xml"):
	xmlname = foldername+"/"+dataset
    # this one is for a single well of projected images
	IJ.run("Calculate pairwise shifts ...", "select=" + xmlname + " process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] method=[Phase Correlation] downsample_in_x=4 downsample_in_y=4")
	IJ.run("Filter pairwise shifts ...", "select=" + xmlname + " min_r=0.6 max_r=1 max_shift_in_x=0 max_shift_in_y=0 max_shift_in_z=0 max_displacement=0")
	IJ.run("Optimize globally and apply shifts ...", "select=" + xmlname + " process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] relative=2.500 absolute=3.500 global_optimization_strategy=[Two-Round using Metadata to align unconnected Tiles] fix_group_0-0")
	IJ.run("Fuse dataset ...", "select=" + xmlname + " process_angle=[All angles] process_channel=[All channels] process_illumination=[All illuminations] process_tile=[All tiles] process_timepoint=[All Timepoints] bounding_box=[Currently Selected Views] downsampling=" +str(downsample) + " pixel_type=[16-bit unsigned integer] interpolation=[Linear Interpolation] image=[Precompute Image] interest_points_for_non_rigid=[-= Disable Non-Rigid =-] blend produce=[Each timepoint & channel] fused_image=[Save as (compressed) TIFF stacks] output_file_directory=" + foldername + " filename_addition=_larged")
  
def has_bigstitcher_dataset(pathname):
	if os.path.isdir(pathname):
		if os.path.exists(pathname+os.path.sep+"dataset.xml"):
			return True
	return False

base = str(basefolder)
files = os.listdir(base)
files = [ base+"/"+f for f in files]
print(files)
big_stitcher_folders= filter(has_bigstitcher_dataset, files)
print(big_stitcher_folders)

print("downsampling by ", downsample)

for folder in big_stitcher_folders:
	print("Processing Folder "+folder)
	process_folder(folder)

print("finished")