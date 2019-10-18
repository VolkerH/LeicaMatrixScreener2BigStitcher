# Selective (smart) acquisition using Leica CAM interface

If the fields to be scanned are only sparsely populated with regions of interest, a lot of acquisition
time can be saved by performing a 2-pass imaging: the first pass is a fast, low-resolution scan. The images
from this scan are then analyzed to find fields that contain the objects of interest and only those fields
are imaged in the slower, high-resolution second pass.