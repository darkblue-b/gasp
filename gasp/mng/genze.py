# -*- coding: utf-8 -*-
from __future__ import unicode_literals

def dissolve(inShp, outShp, fld,
             statistics=None, geomMultiPart=True, api='arcpy', inputIsLines=None):
    """
    Dissolve Geometries
    
    API's Available:
    * arcpy;
    * qgis;
    * saga;
    * ogr;
    * pygrass;
    * grass;
    """
    
    if api == 'arcpy':
        """
        Dissoling geometries with ArcGIS
        """
        
        import arcpy
        
        stat = "" if not statistics else statistics
    
        MULTIPART = "MULTI_PART" if geomMultiPart else "SINGLE_PART"
    
        arcpy.Dissolve_management(inShp, outShp, fld, stat, MULTIPART, "")
    
    elif api == 'qgis':
        import processing
        
        processing.runalg("qgis:dissolve", inShp, False, fld, outShp)
    
    elif api == 'saga':
        """
        Dissolve vectorial data by field
    
        This algorithm doesn't allow self intersections
        """
        
        from gasp import exec_cmd
        
        if not inputIsLines:
            cmd = (
                'saga_cmd shapes_polygons 5 -POLYGONS {in_poly} -FIELDS {fld} '
                '-DISSOLVED {out_shp}'
            ).format(
                in_poly=inShp, fld=fld, out_shp=outShp
            )
        
        else:
            cmd = (
                'saga_cmd shapes_lines 5 -LINES {} -FIELD_1 {} -DISSOLVED {} '
                '-ALL 0'
            ).format(inShp, fld, outShp)
        
        outcmd = exec_cmd(cmd)
    
    elif api == 'ogr':
        """
        Dissolve with OGR and sqlite sql
    
        field_statitics used to preserve numeric fields aggregating their values
        using some statistics
        field_statistics = {fld_name: SUM, fld_name: AVG}
    
        TODO: DISSOLVE WITHOUT FIELD
        """
        
        import os
        from gasp import exec_cmd
        from gasp.oss import get_filename
        
        if not statistics:
            cmd = (
                'ogr2ogr {o} {i} -dialect sqlite -sql '
                '"SELECT ST_Union(geometry), {f} '
                'FROM {t} GROUP BY {f};"'
            ).format(o=outShp, i=inShp, f=fld, t=get_filename(shp))
        
        else:
            cmd = (
                'ogr2ogr {o} {i} -dialect sqlite -sql '
                '"SELECT ST_Union(geometry), {f}, {stat} '
                'FROM {t} GROUP BY {f};"'
            ).format(
                o=outShp, i=inShp, f=fld,
                t=get_filename(shp),
                stat=','.join([
                    '{s}({f}) AS {f}'.format(
                        f=str(fld),
                        s=statistics[fld]
                    ) for fld in statistics]
                )
            )
        
        # Execute command
        outcmd = exec_cmd(cmd)
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        diss = Module(
            "v.dissolve", input=inShp, column=fld, output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        diss()
    
    elif api == 'grass':
        from gasp import exec_cmd
        
        outCmd = exec_cmd((
            "v.dissolve input={}{} output={} "
             "--overwrite --quiet"
        ).format(inShp, " column={}".format(fld) if fld else "", outShp))
    
    else:
        raise ValueError('The api {} is not available'.format(api))
    
    return outShp


def pnd_dissolve(shp, field, outShp):
    """
    Dissolve using GeoPandas
    """
    
    from gasp.fm     import tbl_to_obj
    from gasp.to.shp import df_to_shp
    
    df = tbl_to_obj(shp)
    
    dissDf = df.dissolve(by=field)
    
    return df_to_shp(df, outShp)

