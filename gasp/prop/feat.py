# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Feature Classes Properties
"""

def get_centroid_boundary(shp, isFile=None):
    """
    Return centroid (OGR Point object) of a Boundary (layer with a single
    feature).
    """
    
    from osgeo        import ogr
    from gasp.prop.ff import drv_name
    
    if isFile:
        shp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = shp.GetLayer()
    
        feat = lyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = shp
    
    centroid = geom.Centroid()
    
    cnt = ogr.CreateGeometryFromWkt(centroid.ExportToWkt())
    
    shp.Destroy()
    
    return cnt


def area_to_dic(shp):
    """
    Return the following output:
    
    dic = {
        id_feat: area,
        ...,
        id_feat: area
    }
    """
    
    from osgeo        import ogr
    from gasp.prop.ff import drv_name
    
    o = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    l = o.GetLayer()
    d = {}
    c = 0
    for feat in l:
        g = feat.GetGeometryRef()
        area = g.GetArea()
        d[c] = area
        c += 1
    del l
    o.Destroy()
    return d

