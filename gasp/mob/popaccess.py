"""
Methods to produce Indicators relating Population and their
accessibility to things
"""

"""
Pandas and Google Maps Based Solutions
"""
def gdl_mean_time_wByPop(unities, unities_groups, population_field,
                     destinations, output, workspace=None,
                     unities_epsg=4326,
                     destinations_epsg=4326):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais 
    proxima
    
    # TODO: Migrate to Pandas
    """
    
    import os
    from osgeo               import ogr
    from gasp.prop.ff        import drv_name
    from gasp.fm             import points_to_list
    from gasp.mng.feat       import feat_to_pnt
    from gasp.mng.prj        import project_geom
    from gasp.mng.fld        import add_fields
    from gasp.mng.genze      import dissolve
    from gasp.web.glg.direct import get_time_pnt_destinations
    
    workspace = workspace if workspace else \
        os.path.dirname(output)
    
    # Unities to centroid
    pnt_unities = feat_to_pnt(
        unities,
        os.path.join(
            workspace, 'pnt_' + os.path.basename(unities))
    )
    
    # List destinations
    lst_destinies = points_to_list(
        destinations, listVal="dict",
        inEpsg=destinations_epsg, outEpsg=4326
    )
    
    # Calculate indicator
    polyUnit = ogr.GetDriverByName(
        drv_name(unities)).Open(unities, 1)
    
    polyLyr = polyUnit.GetLayer()
    
    polyLyr = add_fields(polyLyr, {'meantime': ogr.OFTReal})
    
    pntUnit = ogr.GetDriverByName(
        drv_name(pnt_unities)).Open(pnt_unities, 0)
    
    pntLyr = pntUnit.GetLayer()
    
    polyFeat = polyLyr.GetNextFeature()
    distUnities = {}
    groups = {}
    for pntFeat in pntLyr:
        geom = pntFeat.GetGeometryRef()
        
        if unities_epsg == 4326:
            originGeom = geom
        else:
            originGeom = project_geom(geom, unities_epsg, 4326, api='ogr')
        
        _id, duration, distance = get_time_pnt_destinations(
            originGeom, lst_destinies
        )
        
        __min = duration['value'] / 60.0
        pop = polyFeat.GetField(population_field)
        group = polyFeat.GetField(unities_groups)
        
        distUnities[polyFeat.GetFID()] = (__min, __min * pop)
        
        if group not in groups:
            groups[group] = __min * pop
        else:
            groups[group] += __min * pop
        
        polyFeat = polyLyr.GetNextFeature()
    
    del polyLyr
    polyUnit.Destroy()
    
    polyUnit = ogr.GetDriverByName(
        drv_name(unities)).Open(unities, 1)
        
    polyLyr = polyUnit.GetLayer()
    
    for feat in polyLyr:
        unitId = feat.GetFID()
        groupId = feat.GetField(unities_groups)
        
        indicator = (distUnities[unitId][1] / groups[groupId]) * distUnities[unitId][0]
        
        feat.SetField('meantime', indicator)
        
        polyLyr.SetFeature(feat)
    
    del polyLyr, pntLyr
    polyUnit.Destroy()
    pntUnit.Destroy()
    
    dissolve(
        unities, output, unities_groups,
        statistics={'meantime': 'SUM'}, api='ogr'
    )

