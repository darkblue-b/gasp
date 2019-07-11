"""
Sampling tools using OGR Library
"""

from osgeo import ogr
from osgeo import gdal

    

def gdal_point_value_on_raster(pntX, pntY, raster, geotransform=None,
                               rstShape=None):
    """
    Extract, for a given point, the value of a cell with the same location
    """
    
    import os
    import numpy
    
    if type(raster) == str:
        if os.path.isfile(raster):
            img = gdal.Open(raster)
            geo_transform = img.GetGeoTransform()
            band = img.GetRasterBand(1)
        
            if not rstShape:
                tmpArray = numpy.array(band.ReadAsArray())
                nrLnh, nrCols = tmpArray.shape
        
            else:
                nrLnh, nrCols = rstShape
        
        else:
            raise ValueError('Raster is a string but not a file')
    
    else:
        geo_transform = geotransform if geotransform else None
        if not geo_transform:
            raise ValueError(
                'If raster is not a file, geotransform must be specified')
        
        if not rstShape:
            tmpArray = numpy.array(raster.ReadAsArray())
            nrLnh, nrCols = tmpArray.shape
        
        else:
            nrLnh, nrCols = rstShape
        
        band = raster
    
    px = int((pntX - geo_transform[0]) / geo_transform[1])
    py = int((pntY - geo_transform[3]) / geo_transform[5])
    
    if px < 0 or px > nrCols:
        return 0
    
    if py < 0 or py > nrLnh:
        return 0
    
    cell_value = band.ReadAsArray(px, py, 1, 1)
    
    cell_value = float(cell_value) if cell_value else None
    
    return cell_value


def gdal_valuesList_to_pointsList(raster, points_xy):
    import numpy
    
    img = gdal.Open(raster)
    
    geo_transform = img.GetGeoTransform()
    band = img.GetRasterBand(1)
    
    array = numpy.array(band.ReadAsArray())
    lnh, col = array.shape
    
    values = []
    for pnt in points_xy:
        px = int((pnt[0] - geo_transform[0]) / geo_transform[1])
        
        if px < 0 or px > col:
            values.append(-9999)
            continue
        
        py = int((pnt[1] - geo_transform[3]) / geo_transform[5])
        if py < 0 or py > lnh:
            values.append(-9999)
            continue
        
        val = band.ReadAsArray(px, py, 1, 1)
        
        values.append(float(val))
    
    return values


def rst_val_to_points(pnt, rst):
    """
    Extract, for a given point dataset, the value of a cell with the same location
    
    Returns a dict:
    
    d = {
        fid: value,
        ...
    }
    """
    
    from osgeo        import ogr
    from gasp.prop.ff import drv_name
    
    values_by_point = {}
    shp = ogr.GetDriverByName(drv_name(pnt)).Open(pnt, 0)
    lyr = shp.GetLayer()
    
    img = gdal.Open(rst)
    geo_transform = img.GetGeoTransform()
    band = img.GetRasterBand(1)
    
    for feat in lyr:
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        px = int((mx - geo_transform[0]) / geo_transform[1])
        py = int((my - geo_transform[3]) / geo_transform[5])
        
        val_pix = band.ReadAsArray(px, py, 1, 1)
        
        values_by_point[int(feat.GetFID())] = float(val_pix[0][0])
    
    return values_by_point


def rst_val_to_points2(pntShp, listRasters):
    """
    Pick raster value for each point in pntShp
    """
    
    from osgeo        import ogr
    from gasp         import goToList
    from gasp.prop.ff import drv_name
    
    listRasters = goToList(listRasters)
    
    shp = ogr.GetDriverByName(
        drv_name(pntShp)).Open(pnt, 0)
    
    lyr = shp.GetLayer()
    
    pntDict = {}
    for feat in lyr:
        geom = feat.GetGeometryRef()
        
        x, y = geom.GetX(), geom.GetY()
        
        l = []
        for rst in listRasters:
            img = gdal.Open(rst)
            geo_transform = img.GetGeoTransform()
            band = img.GetRasterBand(1)
            
            px = int((x - geo_transform[0]) / geo_transform[1])
            py = int((y - geo_transform[3]) / geo_transform[5])
            value = band.ReadAsArray(px, py, 1, 1)
            
            l.append(list(value)[0])
            
            del img, geo_transform, band, px, py
        
        pntDict[feat.GetFID()] = l
    
    shp.Destroy()
    
    return pntDict

