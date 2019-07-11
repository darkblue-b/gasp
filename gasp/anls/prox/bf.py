"""
Buffering Operations
"""

"""
Memory Based
"""
def geoseries_buffer(gseries, dist):
    """
    Buffer of GeoSeries
    """
    
    return gseries.buffer(dist, resolution=16)


def geodf_buffer_to_shp(geoDf, dist, outfile, colgeom='geometry'):
    """
    Execute the Buffer Function of GeoPandas and export
    the result to a new shp
    """
    
    from gasp.to.shp import df_to_shp
    
    __geoDf = geoDf.copy()
    __geoDf["buffer_geom"] = __geoDf[colgeom].buffer(dist, resolution=16)
    
    __geoDf.drop(colgeom, axis=1, inplace=True)
    __geoDf.rename(columns={"buffer_geom" : colgeom}, inplace=True)
    
    df_to_shp(__geoDf, outfile)
    
    return outfile


def draw_buffer(geom, radius):
    return geom.Buffer(int(round(float(radius), 0)))



"""
File Based
"""
def _buffer(inShp, radius, outShp,
            api='geopandas', dissolve=None, geom_type=None):
    """
    Buffering on Shapefile
    
    API's Available
    * geopandas;
    * saga;
    * grass;
    * pygrass;
    * arcpy;
    """
    
    if api == 'geopandas':
        from gasp.fm import tbl_to_obj
    
        geoDf_ = tbl_to_obj(inShp)
    
        geodf_buffer_to_shp(geoDf_, radius, outShp)
    
    elif api == 'saga':
        """
        A vector based buffer construction partly based on the method supposed by
        Dong et al. 2003. 
        """
        
        from gasp import exec_cmd
        
        distIsField = True if type(radius) == str or type(radius) == unicode \
            else None
        
        c = (
            "saga_cmd shapes_tools 18 -SHAPES {_in} "
            "-BUFFER {_out} {distOption} {d} -DISSOLVE {diss}"
        ).format(
            _in=inShp,
            distOption = "-DIST_FIELD_DEFAULT" if not distIsField else \
                "-DIST_FIELD",
            d=str(radius),
            _out=outShp,
            diss="0" if not dissolve else "1"
        )
        
        outcmd = exec_cmd(c)
    
    elif api=='pygrass':
        from grass.pygrass.modules import Module
        
        if not geom_type:
            raise ValueError((
                'geom_type parameter must have a value when using '
                'pygrass API'
            ))
        
        bf = Module(
            "v.buffer", input=inShp, type=geom_type,
            distance=radius if type(radius) != str else None,
            column=radius if type(radius) == str else None,
            flags='t', output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        bf()
    
    elif api == 'grass':
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.buffer input={} type={} layer=1 {}={} "
            "output={} -t --overwrite --quiet"
        ).format(
            inShp, geom_type,
            "column" if type(radius) == str else "distance",
            str(radius), outShp
        ))
    
    elif api == 'arcpy':
        import arcpy
        
        diss = "NONE" if not dissolve else "LIST" if dissolve != "ALL" and \
            dissolve != "NONE" else dissolve
        
        dissolveCols = None if dissolve != "LIST" else dissolve
        
        arcpy.Buffer_analysis(
            in_features=inShp,
            out_feature_class=outShp,
            buffer_distance_or_field=radius,
            line_side="FULL",
            line_end_type="ROUND",
            dissolve_option=diss,
            dissolve_field=dissolveCols,
            method="PLANAR"
        )
    
    else:
        raise ValueError("{} is not available!".format(api))
    
    return outShp


def buffer_shpFolder(inFolder, outFolder, dist_or_field, fc_format='.shp'):
    """
    Create buffer polygons for all shp in one folder
    """
    
    import os
    from gasp.oss import list_files
    
    lst_fc = list_files(inFolder, file_format=fc_format)
    
    for fc in lst_fc:
        _buffer(
            fc, dist_or_field, os.path.join(outFolder, os.path.basename(fc)),
            api='arcpy' 
        )


def dic_buffer_array_to_shp(arrayBf, outShp, epsg, fields=None):
    """
    Array with dict with buffer proprieties to Feature Class
    """
    
    import os
    from osgeo         import ogr
    from gasp.prop.ff  import drv_name
    from gasp.prop.prj import get_sref_from_epsg
    
    # Get SRS for output
    srs = get_sref_from_epsg(epsg)
    
    # Create output DataSource and Layer
    outData = ogr.GetDriverByName(drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = outData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPolygon
    )
    
    # Create fields
    if fields:
        from gasp.mng.fld import add_fields
        
        add_fields(lyr, fields)
    
    lyrDefn = lyr.GetLayerDefn()
    for _buffer in arrayBf:
        newFeat = ogr.Feature(lyrDefn)
        
        geom = coord_to_buffer(_buffer["X"], _buffer["Y"], _buffer["RADIUS"])
        
        newFeat.SetGeometry(geom)
        
        for field in fields:
            if field in _buffer.keys():
                newFeat.SetField(field, _buffer[field])
        
        lyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
    
    del lyrDefn
    outData.Destroy()
    
    return outShp


def get_sub_buffers(x, y, radius):
    """
    Get Smaller Buffers for each cardeal point (North,
    South, East, West, Northeast, Northwest,
    Southwest and Southeast)
    """
    
    sub_buf = ['north', 'northeast', 'east', 'southeast',
               'south', 'southwest', 'west', 'northwest']
    
    lstSubBuffer = []
    
    for cardeal in sub_buf:
        if cardeal == 'north':
            _y = y + (radius / 2)
        
        elif cardeal == 'northeast' or cardeal == 'northwest':
            _y =  y + ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'south':
            _y = y - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'southeast':
            _y = y - ((radius)**2 / 8.0)**0.5
        
        else:
            _y = y
        
        if cardeal == 'west':
            _x = x - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'northwest':
            _x = x - ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'east':
            _x = x + (radius / 2)
        
        elif cardeal == 'southeast' or cardeal == 'northeast':
            _x = x + ((radius)**2 / 8.0)**0.5
        
        else:
            _x = x
        
        lstSubBuffer.append({
            'X' : _x, 'Y' : _y,
            'RADIUS' : radius / 2,
            'cardeal' : cardeal
        })
    
    return lstSubBuffer

