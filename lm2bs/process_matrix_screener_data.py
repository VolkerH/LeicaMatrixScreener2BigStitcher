# Tools for creating a BigStitcher/BigDataViewer .xml/h5 project file
# from Leica Matrix Screener .ome.tiff output
# 
# Volker . Hilsenstein @ Monash dot Edu
# Sep/Oct 2019
# License BSD-3

import pathlib
import tifffolder
import pandas as pd
import numpy as np
import tifffile
import re
import h5py
from typing import Tuple, Union, List
import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import npy2bdv


def split_pathname(filename: str) -> pd.Series:
    """extracts u,v (well) and x,y (field) coordinates from a matrix screener file name
    
    Parameters
    ----------
    filename : str
        filename of Leica matrix screener tif file 
    
    Returns
    -------
    pd.Series
        pandas series object with u,v,x,y keys
    """
    regex = ".*--U(?P<u>\d+)--V(?P<v>\d+).*--X(?P<x>\d+)--Y(?P<y>\d+)"
    m = re.match(regex, str(filename))
    if m is None:
        raise (RuntimeError, "folder not matching regular expression pattern")
    return pd.to_numeric(pd.Series(m.groupdict()))


def get_meta_from_matrix_ome_tif(filename):
    """ given an ome tif file produced by Leica Matrix Screener,
    return a dictionary with some of the metadata
    """
    tfile = tifffile.TiffFile(filename)
    # print(tfile)
    # note: previous versions of tifffile required
    # thr following step:cd
    # _meta = xmltodict.parse(tfile.ome_metadata)
    _meta = tfile.ome_metadata
    meta = {}
    meta["Size X"] = _meta["Image"]["Pixels"]["SizeX"]
    meta["Size Y"] = _meta["Image"]["Pixels"]["SizeY"]
    meta["PhysicalSize X"] = float(_meta["Image"]["Pixels"]["PhysicalSizeX"])
    meta["PhysicalSize Y"] = float(_meta["Image"]["Pixels"]["PhysicalSizeY"])
    meta["Stage X"] = float(
        _meta["Image"]["Pixels"]["Plane"]["StagePosition"]["PositionX"]
    )
    meta["Stage Y"] = float(
        _meta["Image"]["Pixels"]["Plane"]["StagePosition"]["PositionY"]
    )
    return meta


def get_field(field):
    """ for a given field folder of the leica matrix screener 
    
    Read the stack and return 
      * a numpy like object (Tifffolder)
      * a dictionary with metadata information required for the affine transform matrix
    """
    np_like_array = tifffolder.TiffFolder(field, {"z": "--Z{d2}"})
    first_file = np_like_array.files[0]
    meta = get_meta_from_matrix_ome_tif(first_file)
    return np_like_array, meta


def save_files_for_bigstitcher(
    matrix_screener_fields,
    projected=True,
    volume=True,
    *,
    h5_proj_name=None,
    h5_vol_name=None,
    zspacing=1.0,
    project_func=np.max,
    direction_x=-1,
    direction_y=1,
):
    """
    Save the fields in matrix screener fields as BigStitcher projects

    if volume is True, a project for stitching volumes is created
    if projection is True, a project for stitching projections is creates
    h5_*_name are the outputfilenames for the volume and projection projects
    zspacing is the spacing between z slices in um (cannot find this in metadata)
    project_func is the aggregation function for projections
    direction_* should be either +1 or -1 and can be used to flip coordinate 
    system directions
    """
    print(f"Zspacing: {zspacing}")
    if projected:
        assert h5_proj_name is not None, "h5 output file for projections must be provided"
        bdv_proj_writer = npy2bdv.BdvWriter(
            h5_proj_name,
            nchannels=1,
            ntiles=len(matrix_screener_fields),
            subsamp=((1, 1, 1), (1, 2, 2), (1, 4, 4), (1, 8, 8), (1, 16, 16)),
            blockdim=((1, 64, 64),),
            compression="gzip",
        )  # , (4,4,1)))

    if volume:
        assert h5_vol_name is not None, "h5 output file for volumes must be provided"
        bdv_vol_writer = npy2bdv.BdvWriter(
            h5_vol_name,
            nchannels=1,
            ntiles=len(matrix_screener_fields),
            subsamp=(
                (1, 1, 1),
                (1, 2, 2),
                (1, 4, 4),
                (1, 8, 8),
                (2, 16, 16),
                (4, 32, 32),
            ),
            blockdim=(
                (64, 64, 64),
                (64, 64, 64),
                (64, 64, 64),
                (64, 64, 64),
                (32, 32, 32),
                (16, 16, 16),
            ),
            compression="gzip",
        )

    affine_matrix_template = np.array(
        ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0))
    )

    for tile_nr, field in enumerate(matrix_screener_fields):
        print(f"Processing {tile_nr+1} out of {len(matrix_screener_fields)}:")
        print(field)
        stack, meta = get_field(field)
        affine = affine_matrix_template.copy()
        # Explanation for formula below:
        # Stage position in metadata appears to be in units of metres (m)
        # PhysicalSize appears to be micrometers per voxel (um/vox)
        # therefore for the stageposition in voxel coordinates we need to
        # scale from meters to um (factor 1000000) and then divide by um/vox
        # the direction vectors should be either 1 or -1 and can be used
        # to flip the direction of the coordinate axes.
        affine[1, 3] = (
            meta["Stage X"] * 1_000_000 / meta["PhysicalSize X"] * direction_x
        )  # -2247191 #-2_000_000
        affine[0, 3] = (
            meta["Stage Y"] * 1_000_000 / meta["PhysicalSize Y"] * direction_y
        )  # 2247191 #2_000_000

        if volume:
            bdv_vol_writer.append_view(
                stack,
                time=0,
                channel=0,
                m_affine=affine,
                tile=tile_nr,
                name_affine=f"tile {tile_nr} translation",
                voxel_size_xyz=(meta["PhysicalSize X"], meta["PhysicalSize Y"], zspacing),
                voxel_units="um",
                calibration=(1, 1, zspacing/meta["PhysicalSize X"]),
            )
        if projected:
            outstack = np.expand_dims(project_func(stack, axis=0), axis=0)
            bdv_proj_writer.append_view(
                outstack,
                time=0,
                channel=0,
                m_affine=affine,
                tile=tile_nr,
                name_affine=f"proj. tile {tile_nr} translation",
                # Projections are inherently 2D, so we just repeat the X voxel size for Z
                voxel_size_xyz=(
                    meta["PhysicalSize X"],
                    meta["PhysicalSize Y"],
                    meta["PhysicalSize X"],
                ),
                voxel_units="um",
                # calibration=(1, 1, 1),
            )

    if projected:
        bdv_proj_writer.write_xml_file(ntimes=1)
        bdv_proj_writer.close()
    if volume:
        bdv_vol_writer.write_xml_file(ntimes=1)
        bdv_vol_writer.close()


class Matrix_Mosaic_Processor(object):
    """Holds state and methods to convert files from a Matrix Screener scan for use in BigStitcher 
    """

    def __init__(self, f: Union[str, pathlib.Path]) -> None:
        """initialiaze a Matrix_Mosaic_Processor at the given Matrix Screener folder Path
        
        Parameters
        ----------
        f : Union[str, pathlib.Path]
            Folder location where the matrix screener output files are.
        """
        self.matrix_folder: pathlib.Path = pathlib.Path(f)
        self.df, self.uvwells = self._populate_file_df()

    def __str__(self) -> str:
        r = "Unique wells:\n"
        for i, well in enumerate(self.uvwells):
            r += str(i).zfill(3) + f": {well}\n"
        return r

    def _populate_file_df(self) -> Tuple[pd.DataFrame, list]:
        """ populates data frame with all fields of view comprising the matrix scan experiment
        
        Returns
        -------
        Tuple[pd.DataFrame, list]
            Returns a tuple consisting of a data frame of all fields of view as well 
            as a list of unique (u,v) - well combinations 
        """
        # find all field-- folders
        print("finding fields recurively")
        field_cands = self.matrix_folder.rglob("field*")
        fields = list(filter(lambda x: x.is_dir(), field_cands))
        if fields == []:
            return pd.DataFrame, []
        # find unique chamber-- folders
        chambers = set([f.parent for f in fields])
        # populate data frame
        df = pd.DataFrame(
            data=[map(lambda x: str(x), fields), map((lambda x: str(x.parent)), fields)]
        ).transpose()
        df.columns = ["field", "chamber"]
        df[["u", "v", "x", "y"]] = df["field"].apply(split_pathname)
        df = df.sort_values(["u", "v", "x", "y"])
        # find unique combinations of u,v
        # https://stackoverflow.com/questions/35268817/unique-combinations-of-values-in-selected-columns-in-pandas-data-frame-and-count

        uvcombos = (
            df.groupby(["u", "v"]).size().reset_index().rename(columns={0: "count"})
        )
        uvcombos = uvcombos.sort_values(["u", "v"])
        uvwells = list(zip(uvcombos.u, uvcombos.v))
        print(uvwells)
        return df, uvwells

    def process_well(
        self,
        wellindex: int,
        outfolder_base: pathlib.Path,
        projected: bool,
        volume: bool,
        zspacing: float,
    ):

        u, v = self.uvwells[wellindex]
        h5_proj_name, h5_vol_name = None, None

        print("Processing %d,%d" % (u, v))
        if not (projected or volume):
            print("nothing to do")
            return
        if volume:
            outfolder_vol = outfolder_base / "volume" / f"chamber_{u}_{v}"
            outfolder_vol.mkdir(parents=True, exist_ok=True)
            outfile_vol = outfolder_vol / "dataset.h5"
            h5_vol_name = str(outfile_vol)
        if projected:
            outfolder_proj = outfolder_base / "projection" / f"chamber_{u}_{v}"
            outfolder_proj.mkdir(parents=True, exist_ok=True)
            outfile_proj = outfolder_proj / "dataset.h5"
            h5_proj_name = str(outfile_proj)

        subset = self.df[(self.df.u == u) & (self.df.v == v)]

        save_files_for_bigstitcher(
            subset.field.values,
            projected,
            volume,
            h5_proj_name=h5_proj_name,
            h5_vol_name=h5_vol_name,
            zspacing=zspacing,
        )

    def process_wells(
        self,
        well_indices: List[int],
        outfolder_base: pathlib.Path,
        projected: bool = True,
        volume: bool = False,
        zspacing: float = 1.0,
    ):
        _process = partial(
            self.process_well,
            outfolder_base=outfolder_base,
            projected=projected,
            volume=volume,
            zspacing=zspacing,
        )
        with ThreadPoolExecutor() as p:
            return list(p.map(_process, well_indices))


def test_populate_file_df():
    mp = Matrix_Mosaic_Processor("c:/Users/Volker/Data/Testset/")
    assert not mp.df.empty
    assert isinstance(mp.uvwells, list)


def test_str():
    mp = Matrix_Mosaic_Processor("c:/Users/Volker/Data/Testset/")
    print(mp)


