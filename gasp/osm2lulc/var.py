""" Global Variables """

import os


DB_SCHEMA = {
    "RULES" : {
        "NAME"         : "rules",
        "RULE_ID"      : "fid",
        "RULE_NAME"    : "name"
    },
    "OSM_FEATURES" : {
        "NAME"      : "osm_features",
        "OSM_ID"    : "id",
        "OSM_KEY"   : "key",
        "OSM_VALUE" : "value"
    },
    "CORINE_LAND_COVER"  : {
        "NAME"         : "nom_corine_lc",
        "CLS_ID"       : "clc_id",
        "OSM_RELATION" : "osm_clc",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "clc_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    },
    "URBAN_ATLAS" : {
        "NAME"         : "nom_urban_atlas",
        "CLS_ID"       : "ua_id",
        "OSM_RELATION" : "osm_ua",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "ua_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    },
    "GLOBE_LAND_30"    : {
        "NAME"         : "nom_globe_lc",
        "CLS_ID"       : "globe_id",
        "OSM_RELATION" : "osm_globe",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "globe_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    }
}

PROCEDURE_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'osmtolulc.sqlite'
)

osmTableData = {
    'polygons' : 'multipolygons',
    'lines'    : 'lines',
    'points'   : 'points'
}

PRIORITIES = {
    "URBAN_ATLAS"       : [
        1222, 1221, 12, 5, 14, 13, 11, 2, 3
    ],
    "CORINE_LAND_COVER" : [
        1222, 1221, 12, 5, 4, 14, 13, 11, 22,
        21, 24, 2, 32, 33, 31
    ],
    "GLOBE_LAND_30"     : [
        802, 801, 80, 60, 50, 10, 30, 20, 40, 90, 100
    ],
    "URBAN_ATLAS_NUMPY" : [
        98, 99, 12, 5, 14, 13, 11, 2, 3
    ],
    "CORINE_LAND_COVER_NUMPY" : [
        98, 99, 12, 5, 4, 14, 13, 11, 22, 21, 24, 2, 32, 33, 31
    ],
    "GLOBE_LAND_30_NUMPY" : [
        82, 81, 80, 60, 50, 10, 30, 20, 40, 90, 100
    ]
}

GEOM_AREA = "geom_area"

LEGEND = {
    "URBAN_ATLAS" : {
        1222 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        1221 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2 : "Agricultural, semi-natural areas, wetlands",
        3 : "Forests",
        5 : "Water"
    },
    "CORINE_LAND_COVER" : {
        1222 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        1221 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2  : "Agricultural areas",
        21 : "Arable Land",
        22 : "Permanent crops",
        23 : "Pastures",
        24 : "Heterogeneous",
        31 : "Forests",
        32 : "Scrub and/or herbaceous vegetation associations",
        33 : "Open spaces with little or no vegetation",
        5  : "Water",
        4  : "Wetlands"
    },
    "GLOBE_LAND_30" : {
        801 : "Artificial surfaces",
        802 : "Artificial surfaces",
        80  : "Artificial surfaces",
        60  : "Water bodies",
        50  : "Wetland",
        10  : "Cultivated land",
        30  : "Grassland",
        20  : "Forests",
        40  : "Scrubland",
        90  : "Bareland",
        70  : "Tundra",
        100 : "Permanent snow/ice"
    },
    "URBAN_ATLAS_NUMPY" : {
        98 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        99 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2 : "Agricultural, semi-natural areas, wetlands",
        3 : "Forests",
        5 : "Water"
    },
    "CORINE_LAND_COVER_NUMPY" : {
        98 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        99 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2  : "Agricultural areas",
        21 : "Arable Land",
        22 : "Permanent crops",
        23 : "Pastures",
        24 : "Heterogeneous",
        31 : "Forests",
        32 : "Scrub and/or herbaceous vegetation associations",
        33 : "Open spaces with little or no vegetation",
        5  : "Water",
        4  : "Wetlands"
    },
    "GLOBE_LAND_30_NUMPY" : {
        82  : "Artificial surfaces",
        81  : "Artificial surfaces",
        80  : "Artificial surfaces",
        60  : "Water bodies",
        50  : "Wetland",
        10  : "Cultivated land",
        30  : "Grassland",
        20  : "Forests",
        40  : "Scrubland",
        90  : "Bareland",
        70  : "Tundra",
        100 : "Permanent snow/ice"
    }
}