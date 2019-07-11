"""
Processing Raster data with GDAL
"""


def raster_rotation(inFolder, template, outFolder, img_format='.tif'):
    """
    Invert raster data
    """
    
    import os
    from osgeo         import gdal
    from gasp.oss      import list_files
    from gasp.fm.rst   import rst_to_array
    from gasp.prop.rst import get_nodata
    from gasp.to.rst   import array_to_raster
    
    rasters = list_files(inFolder, file_format=img_format)
    
    for rst in rasters:
        a  = rst_to_array(rst)
        nd = get_nodata(rst, gisApi='gdal')
        
        array_to_raster(
            a[::-1],
            os.path.join(outFolder, os.path.basename(rst)),
            template, None, gdal.GDT_Float32, noData=nd,
            gisApi='gdal'
        )


def composite(bndRed, bndGreen, bndBlue, outrst, ascmd=None):
    """
    r.composite - Combines red, green and blue raster maps into
    a single composite raster map.
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        rcom = Module(
            "r.composite", red=bndRed, green=bndGreen, blue=bndBlue,
            output=outrst, overwrite=True, run_=False
        )
        
        rcom()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.composite red={} green={} blue={} output={} --overwrite"
        ).format(bndRed, bndGreen, bndBlue, outrst))
    
    return outrst

