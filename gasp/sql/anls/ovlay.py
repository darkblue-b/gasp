"""
Overlay operations with PostGIS
"""


def intersect_in_same_table(conParam, table, geomA, geomB, outtable,
                            intersectField='intersects',
                            intersectGeom=None, colsSel=None):
    """
    Intersect two Geometries in the same table
    """
    
    from gasp            import goToList
    from gasp.sql.c      import psqlcon
    from gasp.sql.mng.qw import ntbl_by_query
    
    COLS = goToList(colsSel)
    
    return ntbl_by_query(
        conParam, outtable,
        ("SELECT {cls}, CASE WHEN interse IS TRUE THEN 1 ELSE 0 END AS {intF} "
         "{intgeomF}FROM ("
            "SELECT {cls}, ST_Intersects({gA}, {gB}) AS interse "
            "{intgeom}FROM {t}"
         ") AS tst").format(
             gA=geomA, gB=geomB, t=table, intF=intersectField,
             cls="*" if not COLS else ", ".join(COLS),
             intgeom= "" if not intersectGeom else \
                ", ST_Intersection({}, {}) AS intersect_geom".format(
                    geomA, geomB
                ),
            intgeomF = "" if not intersectGeom else ", intersect_geom"
        ), api='psql'
    )


def del_topoerror_shps(conParam, shps, epsg, outfolder):
    """
    Remove topological errors from Feature Class data using PostGIS
    """
    
    import os
    from gasp             import goToList
    from gasp.sql.mng.fld import cols_name
    from gasp.sql.mng.qw  import ntbl_by_query
    from gasp.to.sql      import shp_to_psql
    from gasp.to.shp      import psql_to_shp
    
    shps = goToList(shps)
    
    TABLES = shp_to_psql(conParam, shps, epsg, api="shp2pgsql")
    
    NTABLE = [ntbl_by_query(
        conParam, "nt_{}".format(t),
        "SELECT {cols}, ST_MakeValid({tbl}.geom) AS geom FROM {tbl}".format(
            cols = ", ".join(["{}.{}".format(TABLES[t], x) for x in cols_name(
                conParam, TABLES[t], sanitizeSpecialWords=None
            ) if x != 'geom']),
            tbl=TABLES[t]
        ), api='psql'
    ) for t in range(len(TABLES))]
    
    for t in range(len(NTABLE)):
        psql_to_shp(
            conParam, NTABLE[t],
            os.path.join(outfolder, TABLES[t]), tableIsQuery=None,
            api='pgsql2shp', geom_col="geom"
        )


def intersection(lnk, aShp, bShp, pk, aGeom, bGeom, output,
                 primitive, priority, new_pk='fid_pk', new_geom='geom'):
    """
    Intersect two layers

    primitive is the geometric primitive (point, line, polygons)

    priority is an indication of the fields that the user wants to include in
    the output - fields of aShp or fields of bShp.
    The user could giver a list (with fields for selection) as value for the
    priority argument.
    """
    
    from gasp.sql.mng.fld import cols_name

    if priority == 'a':
        cols_tbl = cols_name(lnk, aShp)
        cols_tbl.remove(aGeom)
    elif priority == 'b':
        cols_tbl = cols_name(lnk, bShp)
        cols_tbl.remove(bGeom)
    elif type(priority) == type([0]):
        cols_tbl = priority
    cols_tbl.remove(pk)
    conn = psqlcon(
        lnk['HOST'], lnk['USER'], lnk['PASSWORD'],
        lnk['PORT'], lnk['DATABASE']
    )
    cursor = conn.cursor()

    if primitive == 'point':
        cols_tbl = ['{t}.{c}'.format(t=aShp, c=x) for x in cols_tbl]
        if priority == 'a':
            sel_geom = "{f}.{g}".format(f=aShp, g=aGeom)
        elif priority == 'b' or type(priority) == type([]):
            sel_geom = "{f}.{g}".format(f=bShp, g=bGeom)
        cursor.execute((
            "CREATE TABLE {out} AS SELECT {cols}, {int_geom} AS {ngeom} FROM {pnt} "
            "INNER JOIN {poly} ON ST_Within({pnt}.{geom_a}, "
            "{poly}.{geom_b});").format(
                out=output,
                cols=','.join(cols_tbl),
                pnt=aShp,
                geom_a=aGeom,
                geom_b=bGeom,
                poly=bShp,
                int_geom=sel_geom, ngeom=new_geom
        ))

    elif primitive == 'line':
        cols_tbl = ['{t}.{c}'.format(t=output, c=x) for x in cols_tbl]
        cols_tbl.append(new_geom)
        cursor.execute((
            "CREATE TABLE {out} AS SELECT {cols} FROM (SELECT {shp_a}.*, "
            "(ST_DUMP(ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}))).geom "
            "FROM {shp_b} INNER JOIN {shp_a} ON ST_Intersects({shp_b}.geom, "
            "{shp_a}.{geom_fld})) As {out} WHERE ST_Dimension({out}.geom) = "
            "1;").format(
                out=output,
                cols=','.join(cols_tbl),
                shp_a=aShp,
                shp_b=bShp,
                geom_fld=aGeom
        ))

    elif primitive == 'polygon':
        cols_tbl = ['{t}.{c}'.format(t=aShp, c=x) for x in cols_tbl]
        cursor.execute((
            'CREATE TABLE {out} AS SELECT {cols}, ST_Multi(ST_Buffer'
            '(ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}), 0.0)) As '
            '{ngeom} FROM {shp_b} INNER JOIN {shp_a} ON ST_Intersects({shp_b}.geom, '
            '{shp_a}.{geom_fld}) WHERE Not ST_IsEmpty(ST_Buffer('
            'ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}), 0.0));').format(
                out=output,
                cols=','.join(cols_tbl),
                shp_a=aShp,
                shp_b = bShp,
                geom_fld=aGeom, ngeom=new_geom
        ))

    cursor.execute(
        "ALTER TABLE {out} ADD COLUMN {fid_pk} BIGSERIAL PRIMARY KEY;".format(
            out=output, fid_pk=new_pk))

    conn.commit()
    cursor.close()
    conn.close()
    return output, new_pk, new_geom


def proj_clean_clip(con, dic_osm, boundary, srs, workspace):
    """
    1. Reproject all osm tables to a specified spatial reference system
    
    The procedure expects projected coordinates
    
    2. Clean some topologic errors
    
    3. Clip osm data for the boundary
    """
    
    irrevelant_cols = [
        'addr:housename', 'addr:housenumber', 'addr:interpolation',
        'generator:source', 'tower:type'
    ]
    
    if os.path.splitext(boundary)[1] != '.shp':
        from gasp.to.shp import shp_to_shp
        
        boundary = shp_to_shp(
            boundary, os.path.join(workspace, 'lmt.shp'),
            gisApi='ogr'
        )
    
    from gasp.to.sql import shp_to_psql_tbl
    lmt_table = shp_to_psql(con, boundary, srs, api='shp2pgsql')
    lmt_geom = "geom"
    
    from gasp.sql.mng.prj    import re_project
    from gasp.sql.anls.ovlay import intersection
    from gasp.sql.anls.ovlay import topologic_correction
    
    for k in dic_osm:
        proj_table, pk, geom = re_project(
            con, dic_osm[k], 'way', str(srs),
            'proj_' + k, del_cols=irrevelant_cols
        )
        
        clean_table, pk, geom = topologic_correction(
            con, proj_table, pk, geom, 'clean_' + k
        )
        
        clip_table, pk, geom = intersection(
            con, clean_table, lmt_table, pk, geom, lmt_geom, 'clip_' + k,
            k, 'a'
        )
        
        dic_osm[k] = [clip_table, pk, geom]
    
    return dic_osm


def check_autofc_overlap(checkShp, epsg, conParam, outOverlaps):
    """
    Check if the features of one Feature Class overlaps each other
    """
    
    import os
    
    from gasp.sql.mng.db import create_db
    from gasp.sql.mng.qw import ntbl_by_query
    from gasp.to.sql     import shp_to_psql_tbl
    from gasp.to.shp     import psql_to_shp
    
    create_db(conParam, conParam["DB"])
    conParam["DATABASE"] = conParam["DB"]
    
    # Send data to postgresql
    table = shp_to_psql(conParam, checkShp, epsg, api="pandas")
    
    # Produce result
    q = (
        "SELECT foo.* FROM ("
            "SELECT * FROM {t}"
        ") AS foo, ("
            "SELECT cat AS relcat, geom AS tst_geom FROM {t}"
        ") AS foo2 "
        "WHERE ("
            "ST_Overlaps(geom, tst_geom) IS TRUE OR "
            "ST_Equals(geom, tst_geom) IS TRUE OR "
            "ST_Contains(geom, tst_geom) IS TRUE"
        ") AND cat <> relcat"
    ).format(t=table)
    
    resultTable = os.path.splitext(os.path.basename(outOverlaps))[0]
    ntbl_by_query(conParam, resultTable, q, api='psql')
    
    psql_to_shp(conParam, resultTable, outOverlaps, api='pandas', epsg=epsg)
    
    return outOverlaps


def pg_erase(conParam, inTbl, eraseTbl, inGeom, eraseGeom, outTbl):
    """
    Erase
    """
    
    from gasp.sql.mng.fld import cols_name
    from gasp.sql.mng.qw import ntbl_by_query
    
    cols = ["mtbl.{}".format(
        x) for x in cols_name(conParam, inTbl, api='psql') if x != inGeom]
    
    q = (
        "SELECT {}, ST_Difference(mtbl.{}, foo.erase_geom) AS {} "
        "FROM {} AS mtbl, "
        "("
            "SELECT ST_UnaryUnion(ST_Collect(eetbl.{})) AS erase_geom "
            "FROM {} AS eetbl "
            "INNER JOIN {} AS jtbl ON ST_Intersects(eetbl.{}, jtbl.{})"
        ") AS foo"
    ).format(
        ", ".join(cols), inGeom, inGeom, inTbl, eraseGeom, eraseTbl,
        inTbl, eraseGeom, inGeom
    )
    
    return ntbl_by_query(conParam, outTbl, q, api='psql')
    
"""
OGR Overlay with SpatialLite
"""

def intersect_point_with_polygon(sqDB, pntTbl, pntGeom,
                                 polyTbl, polyGeom, outTbl,
                                 pntSelect=None, polySelect=None,
                                 pntQuery=None, polyQuery=None,
                                 outTblIsFile=None):
    """
    Intersect Points with Polygons
    
    What TODO with this?
    """
    
    import os
    
    if not pntSelect and not polySelect:
        raise ValueError("You have to select something")
    
    sql = (
        "SELECT {colPnt}{colPoly} FROM {pnt_tq} "
        "INNER JOIN {poly_tq} ON "
        "ST_Within({pnt}.{pnGeom}, {poly}.{pgeom})"
    ).format(
        colPnt  = pntSelect if pntSelect else "",
        colPoly = polySelect if polySelect and not pntSelect else \
            ", " + polySelect if polySelect and pntSelect else "",
        pnt_tq  = pntTbl if not pntQuery else pntQuery,
        poly_tq = polyTbl if not polyQuery else polyQuery,
        pnt     = pntTbl,
        poly    = polyTbl,
        pnGeom  = pntGeom,
        pgeom   = polyGeom
    )
    
    if outTblIsFile:
        from gasp.anls.exct import sel_by_attr
        
        sel_by_attr(sqDB, sql, outTbl, api_gis='ogr')
    
    else:
        from gasp.sql.mng.qw import ntbl_by_query
        
        ntbl_by_query(sqDB, outTbl, sql, api='ogr2ogr')


def disjoint_polygons_rel_points(sqBD, pntTbl, pntGeom,
                                polyTbl, polyGeom, outTbl,
                                polySelect=None,
                                pntQuery=None, polyQuery=None,
                                outTblIsFile=None):
    """
    Get Disjoint relation
    
    What TODO with this?
    """
    
    import os
    
    if not polySelect:
        raise ValueError("Man, select something!")
    
    sql = (
        "SELECT {selCols} FROM {polTable} WHERE ("
        "{polName}.{polGeom} not in ("
            "SELECT {polName}.{polGeom} FROM {pntTable} "
            "INNER JOIN {polTable} ON "
            "ST_Within({pntName}.{pntGeom_}, {polName}.{polGeom})"
        "))"
    ).format(
        selCols  = "*" if not polySelect else polySelect,
        polTable = polyTbl if not polyQuery else polyQuery,
        polGeom  = polyGeom,
        pntTable = pntTbl if not pntQuery else pntQuery,
        pntGeom_ = pntGeom,
        pntName  = pntTbl,
        polName  = polyTbl
    )
    
    if outTblIsFile:
        from gasp.anls.exct import sel_by_attr
        
        sel_by_attr(sqBD, sql, outTbl, api_gis='ogr')
    
    else:
        from gasp.sql.mng.qw import ntbl_by_query
        
        ntbl_by_query(sqBD, outTbl, sql, api='ogr2ogr')


def sgbd_get_feat_within(conParam, inTbl, inGeom, withinTbl, withinGeom, outTbl,
                         inTblCols=None, withinCols=None, outTblIsFile=None,
                         apiToUse='OGR_SPATIALITE'):
    """
    Get Features within other Geometries in withinTbl
    e.g. Intersect points with Polygons
    
    apiToUse options:
    * OGR_SPATIALITE;
    * POSTGIS.
    """
    
    from gasp import goToList
    
    if not inTblCols and not withinCols:
        colSelect = "intbl.*, witbl.*"
    else:
        if inTblCols and not withinCols:
            colSelect = ", ".join([
                "intbl.{}".format(c) for c in goToList(inTblCols)
            ])
        
        elif not inTblCols and withinCols:
            colSelect = ", ".join([
                "witbl.{}".format(c) for c in goToList(withinCols)
            ])
        
        else:
            colSelect = "{}, {}".format(
                ", ".join(["intbl.{}".format(c) for c in goToList(inTblCols)]),
                ", ".join(["witbl.{}".format(c) for c in goToList(withinCols)])
            )
    
    Q = (
        "SELECT {selcols} FROM {in_tbl} AS intbl "
        "INNER JOIN {within_tbl} AS witbl ON "
        "ST_Within(intbl.{in_geom}, witbl.{wi_geom})"
    ).format(
        selcols=colSelect, in_tbl=inTbl, within_tbl=withinTbl,
        in_geom=inGeom, wi_geom=withinGeom
    )
    
    if apiToUse == "OGR_SPATIALITE":
        if outTblIsFile:
            from gasp.anls.exct import sel_by_attr
            
            sel_by_attr(conParam, Q, outTbl, api_gis='ogr')
        
        else:
            from gasp.sql.mng.qw import ntbl_by_query
            
            ntbl_by_query(conParam, outTbl, Q, api='ogr2ogr')
    
    elif apiToUse == 'POSTGIS':
        if outTblIsFile:
            from gasp.to.shp import psql_to_shp
            
            psql_to_shp(
                conParam, Q, outTbl, api="pgsql2shp",
                geom_col=None, tableIsQuery=True)
        
        else:
            from gasp.sql.mng.qw import ntbl_by_query
            
            ntbl_by_query(conParam, outTbl, Q, api='psql')
    
    else:
        raise ValueError((
            "API {} is not available. OGR_SPATIALITE and POSTGIS "
            "are the only valid options"
        ))
    
    return outTbl


def sgbd_get_feat_not_within(dbcon, inTbl, inGeom, withinTbl, withinGeom, outTbl,
                             inTblCols=None, outTblIsFile=None,
                             apiToUse='OGR_SPATIALITE'):
    """
    Get features not Within with any of the features in withinTbl
    
    apiToUse options:
    * OGR_SPATIALITE;
    * POSTGIS.
    """
    
    from gasp import goToList
    
    Q = (
        "SELECT {selCols} FROM {tbl} AS in_tbl WHERE ("
        "in_tbl.{in_geom} NOT IN ("
            "SELECT inin_tbl.{in_geom} FROM {wi_tbl} AS wi_tbl "
            "INNER JOIN {tbl} AS inin_tbl ON "
            "ST_Within(wi_tbl.{wi_geom}, inin_tbl.{in_geom})"
        "))"
    ).format(
        selCols = "*" if not inTblCols else ", ".join(goToList(inTblCols)),
        tbl     = inTbl,
        in_geom = inGeom,
        wi_tbl  = withinTbl,
        wi_geom = withinGeom
    )
    
    if apiToUse == "OGR_SPATIALITE":
        if outTblIsFile:
            from gasp.anls.exct import sel_by_attr
            
            sel_by_attr(dbcon, Q, outTbl, api_gis='ogr')
        
        else:
            from gasp.sql.mng.qw import ntbl_by_query
            
            ntbl_by_query(dbcon, outTbl, Q, api='ogr2ogr')
    
    elif apiToUse == "POSTGIS":
        if outTblIsFile:
            from gasp.to.shp import psql_to_shp
            
            psql_to_shp(
                dbcon, Q, outTbl, api='pgsql2shp',
                geom_col=None, tableIsQuery=True
            )
        
        else:
            from gasp.sql.mng.qw import ntbl_by_query
            
            ntbl_by_query(dbcon, outTbl, Q, api='psql')
    
    else:
        raise ValueError((
            "API {} is not available. OGR_SPATIALITE and POSTGIS "
            "are the only valid options"
        ))
    
    return outTbl
