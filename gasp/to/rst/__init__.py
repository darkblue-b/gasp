# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
To raster tools
"""


"""
Raster to Raster tools
"""

def composite_bnds(rsts, outRst, epsg=None, gisAPI='gdal'):
    """
    Composite Bands
    
    API's Available:
    * gdal;
    """
    
    if gisAPI == 'gdal':
        """
        Using GDAL
        """
        
        from osgeo         import gdal
        from gasp.fm.rst   import rst_to_array
        from gasp.prop.ff  import drv_name
        from gasp.prop.rst import rst_dataType, get_nodata
        
        # Get Arrays
        _as = [rst_to_array(r) for r in rsts]
        
        # Get nodata values
        nds = [get_nodata(r, gisApi='gdal') for r in rsts]
        
        # Open template and get some metadata
        img_temp = gdal.Open(rsts[0])
        geo_tran = img_temp.GetGeoTransform()
        band     = img_temp.GetRasterBand(1)
        dataType = rst_dataType(band)
        rows, cols = _as[0].shape
        
        # Create Output
        drv = gdal.GetDriverByName(drv_name(outRst))
        out = drv.Create(outRst, cols, rows, len(_as), dataType)
        out.SetGeoTransform(geo_tran)
        
        if epsg:
            from gasp.prop.prj import epsg_to_wkt
            srs = epsg_to_wkt(epsg)
            out.SetProjection(srs)
        
        # Write all bands
        for i in range(len(_as)):
            outBand = out.GetRasterBand(i + 1)
            
            outBand.SetNoDataValue(nds[i])
            outBand.WriteArray(_as[i])
            
            outBand.FlushCache()
    
    else:
        raise ValueError('The api {} is not available'.format(gisAPI))
    
    return outRst


"""
Change data format
"""

def rst_to_rst(inRst, outRst):
    """
    Convert a raster file to another raster format
    """
    
    from gasp         import exec_cmd
    from gasp.prop.ff import drv_name
    
    outDrv = drv_name(outRst)
    cmd = 'gdal_translate -of {drv} {_in} {_out}'.format(
        drv=outDrv, _in=inRst, _out=outRst
    )
    
    cmdout = exec_cmd(cmd)
    
    return outRst


def folder_nc_to_tif(inFolder, outFolder):
    """
    Convert all nc existing on a folder to GTiff
    """
    
    import netCDF4;     import os
    from gasp.oss       import list_files
    from gasp.mng.split import gdal_split_bands
    
    # List nc files
    lst_nc = list_files(inFolder, file_format='.nc')
    
    # nc to tiff
    for nc in lst_nc:
        # Check the number of images in nc file
        datasets = []
        _nc = netCDF4.Dataset(nc, 'r')
        for v in _nc.variables:
            if v == 'lat' or v == 'lon':
                continue
            lshape = len(_nc.variables[v].shape)
            if lshape >= 2:
                datasets.append(v)
        # if the nc has any raster
        if len(datasets) == 0:
            continue
        # if the nc has only one raster
        elif len(datasets) == 1:
            output = os.path.join(
                outFolder,
                os.path.basename(os.path.splitext(nc)[0]) + '.tif'
            )
            rst_to_rst(nc, output)
            gdal_split_bands(output, outFolder)
        # if the nc has more than one raster
        else:
            for dts in datasets:
                output = os.path.join(
                    outFolder,
                    '{orf}_{v}.tif'.format(
                        orf = os.path.basename(os.path.splitext(nc)[0]),
                        v = dts
                    )
                )
                rst_to_rst(
                    'NETCDF:"{n}":{v}'.format(n=nc, v=dts),
                    output
                )
                gdal_split_bands(output, outFolder)


def shape_to_rst_wShapeCheck(inShp, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Feature Class to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os
    from gasp          import goToList
    from gasp.prop.rst import rst_shape
    
    desiredCellsizes = goToList(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    workspace = os.path.dirname(outRst)
    
    RASTERS = [shp_to_raster(
        inShp, cellsize, -1, os.path.join(
            workspace, 'tst_cell_{}.tif'.format(cellSize)
        ), inEPSG
    ) for cellSize in desiredCellsizes]
    
    tstShape = rst_shape(RASTERS, gisApi='gdal')
    
    for rst in tstShape:
        NCELLS = tstShape[rst][0] * tstShape[rst][1]
        tstShape[rst] = NCELLS
    
    NICE_RASTER = None
    for i in range(len(desiredCellsizes)):
        if tstShape[RASTERS[i]] <= maxCellNumber:
            NICE_RASTER = RASTERS[i]
            break
        
        else:
            continue
    
    if not NICE_RASTER:
        return None
    
    else:
        os.rename(NICE_RASTER, outRst)
        
        for rst in RASTERS:
            if os.path.isfile(rst) and os.path.exists(rst):
                os.remove(rst)
        
        return outRst

