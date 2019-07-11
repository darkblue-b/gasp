"""
Data to ESRI Shapefile
"""


def obj_to_shp(dd, geomkey, srs, outshp):
    from gasp.to.obj import obj_to_geodf
    
    geodf = obj_to_geodf(dd, geomkey, srs)
    
    return df_to_shp(geodf, outshp)


def pointXls_to_shp(xlsFile, outShp, x_col, y_col, epsg, sheet=None):
    """
    Excel table with Point information to ESRI Shapefile
    """
    
    from gasp.fm      import tbl_to_obj
    from gasp.to.geom import pnt_dfwxy_to_geodf
    from gasp.to.shp  import df_to_shp
    
    # XLS TO PANDAS DATAFRAME
    dataDf = tbl_to_obj(xlsFile, sheet=sheet)
    
    # DATAFRAME TO GEO DATAFRAME
    geoDataDf = pnt_dfwxy_to_geodf(dataDf, x_col, y_col, epsg)
    
    # GEODATAFRAME TO ESRI SHAPEFILE
    df_to_shp(geoDataDf, outShp)
    
    return outShp


"""
Raster to Feature Class
"""

def rst_to_polyg(inRst, outShp, rstColumn=None, gisApi='gdal', epsg=None):
    """
    Raster to Polygon Shapefile
    
    Api's Available:
    * arcpy;
    * gdal;
    * qgis;
    * pygrass;
    * grasscmd
    """
    
    if gisApi == 'arcpy':
        rstField = 'Value' if not rstColumn else rstColumn
        
        import arcpy
        
        arcpy.RasterToPolygon_conversion(
            in_raster=inRst, 
            out_polygon_features=outShp, 
            simplify=None, 
            raster_field=rstField
        )
    
    elif gisApi == 'gdal':
        if not epsg:
            raise ValueError((
                'Using GDAL, you must specify the EPSG CODE of the '
                'Spatial Reference System of input raster.'
            ))
        
        import os
        from osgeo        import gdal, ogr, osr
        from gasp.prop.ff import drv_name
        from gasp.oss     import get_filename
        
        src = gdal.Open(inRst)
        bnd = src.GetRasterBand(1)
        
        output = ogr.GetDriverByName(drv_name(ouShp)).CreateDataSource(outShp)
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        
        lyr = output.CreateLayer(get_filename(outShp, forceLower=True), srs)
        
        lyr.CreateField(ogr.FieldDefn('VALUE', ogr.OFTInteger))
        gdal.Polygonize(bnd, None, lyr, 0, [], callback=None)
        
        output.Destroy()
    
    elif gisApi == 'qgis':
        import processing
        
        processing.runalg(
            "gdalogr:polygonize", inRst, "value", outShp
        )
    
    elif gisApi == 'pygrass':
        from grass.pygrass.modules import Module
        
        rstField = "value" if not rstColumn else rstColumn
        
        rtop = Module(
            "r.to.vect", input=inRst, output=outShp, type="area",
            column=rstField, overwrite=True, run_=False, quiet=True
        )
        rtop()
    
    elif gisApi == 'grasscmd':
        from gasp import exec_cmd
        
        rstField = "value" if not rstColumn else rstColumn
        
        rcmd = exec_cmd((
            "r.to.vect input={} output={} type=area column={} "
            "--overwrite --quiet"
        ).format(inRst, outShp, rstField))
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp

