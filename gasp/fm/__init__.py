"""
Tables to Pandas DataFrame
"""

def points_to_list(pntShp, listVal='tuple', inEpsg=None, outEpsg=None):
    """
    Return a list as:
    
    if listVal == 'tuple'
    l = [(x_coord, y_coord), ..., (x_coord, y_coord)]
    
    elif listVal == 'dict'
    l = [
        {id : fid_value, x : x_coord, y : y_coord},
        ...
        {id : fid_value, x : x_coord, y : y_coord}
    ]
    """
    
    geoDf = tbl_to_obj(pntShp)
    
    if inEpsg and outEpsg:
        if inEpsg != outEpsg:
            from gasp.mng.prj import project
            geoDf = project(geoDf, None, outEpsg, gisApi='pandas')
    
    geoDf["x"] = geoDf.geometry.x.astype(float)
    geoDf["y"] = geoDf.geometry.y.astype(float)
    
    if listVal == 'tuple':
        subset = geoDf[['x', 'y']]
    
        coords = [tuple(x) for x in subset.values]
    
    elif listVal == 'dict':
        geoDf["id"] = geoDf.index
        subset = geoDf[['id', 'x', 'y']]
        
        coords = subset.to_dict(orient='records')
    
    else:
        raise ValueError(
            'Value of listVal is not Valid. Please use "tuple" or "dict"'
        )
    
    return coords

