"""
Tools for Geoserver layers management
"""


def list_layers(conf={
    'USER':'admin', 'PASSWORD': 'geoserver',
    'HOST':'localhost', 'PORT': '8080'
    }, protocol='http'):
    """
    List all layers in the geoserver
    """

    import requests

    url = '{pro}://{host}:{port}/geoserver/rest/layers'.format(
        host=conf['HOST'], port=conf['PORT'], pro=protocol
    )

    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    layers = r.json()

    return [l['name'] for l in layers['layers']['layer']]


def publish_postgis_layer(workspace, store, pg_table, title=None, gs_con={
        'USER':'admin', 'PASSWORD': 'geoserver',
        'HOST':'localhost', 'PORT': '8888'
    }, protocol='http'):
    """
    Publish PostGIS table in geoserver
    """
    
    import os
    import requests
    
    from gasp.oss.ops import create_folder, del_folder
    from gasp         import random_str
    from gasp.to.Xml  import write_xml_tree
    
    # Create folder to write xml
    wTmp = create_folder(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), random_str(7)
        )
    )
    
    # Create obj with data to be written in the xml
    lyr_title = "Title {}".format(pg_table) if not title else title
    elements = {
        "featureType": {
            "name"  : pg_table,
            "title" : lyr_title
        }
    }
    
    # Write the xml
    xml_file = write_xml_tree(
        elements,
        os.path.join(wTmp, '{}.xml'.format(pg_table))
    )
    
    # Create Geoserver Layer
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{wname}/'
        'datastores/{store_name}/featuretypes'
    ).format(
        host=gs_con['HOST'], port=gs_con['PORT'], wname=workspace,
        store_name=store, pro=protocol
    )
    
    with open(xml_file, 'rb') as __xml:
        r = requests.post(
            url, data=__xml, headers={'content-type': 'text/xml'},
            auth=(gs_con['USER'], gs_con['PASSWORD'])
        )
        
        __xml.close()
    
    del_folder(wTmp)
    
    return r


def publish_raster_layer(layername, datastore, workspace, epsg_code, conf={
        'USER': 'admin', 'PASSWORD': 'geoserver',
        'HOST': 'localhost', 'PORT': '8888'
    }, protocol='http'):
    """
    Publish a Raster layer
    """
    
    import os;         import requests
    from gasp.to.Xml   import write_xml_tree
    from gasp          import random_str
    from gasp.oss.ops  import create_folder, del_folder
    from gasp.prop.prj import epsg_to_wkt
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'coveragestores/{storename}/coverages'
    ).format(
        host=conf['HOST'], port=conf['PORT'],
        work=workspace, storename=datastore, pro=protocol
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {
        "coverage" : {
            "name"      : layername,
            "title"     : layername,
            "nativeCRS" : str(epsg_to_wkt(epsg_code)),
            "srs"       : 'EPSG:{}'.format(str(epsg_code)),
        }
    }
    
    # Write XML
    wTmp = create_folder(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            random_str(7)
        )
    ) 
    
    xml_file = write_xml_tree(
        xmlTree, os.path.join(wTmp, 'rst_lyr.xml')
    )
    
    # Create layer
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url, data=f,
            headers={'content-type': 'text/xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    del_folder(wTmp)
    
    return r

