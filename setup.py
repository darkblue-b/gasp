#from distutils.core import setup
from setuptools import setup

setup(
    name='gasp',
    version='0.0.1',
    description='GASP',
    url='https://github.com/jasp382/gasp',
    author='jasp382',
    author_email='joaquimaspatriarca@gmail.com',
    license='GPL',
    packages=[
        # Main module
        'gasp',
        # ******************************************************************** #
        'gasp.anls', 'gasp.anls.prox',
        # ******************************************************************** #
        'gasp.dt',
        # ******************************************************************** #
        'gasp.fm',
        # ******************************************************************** #
        'gasp.mng', 'gasp.mng.fld', 'gasp.mng.xlstbx',
        # ******************************************************************** #
        'gasp.mob', 'gasp.mob.api', 'gasp.mob.api.glg', 'gasp.mob.grstbx',
        # ******************************************************************** #
        'gasp.osm2lulc', 'gasp.osm2lulc.utils',
        # ******************************************************************** #
        'gasp.oss',
        # ******************************************************************** #
        'gasp.prop',
        # ******************************************************************** #
        'gasp.spanlst',
        # ******************************************************************** #
        'gasp.sql', 'gasp.sql.anls', 'gasp.sql.charts', 'gasp.sql.mng',
        # ******************************************************************** #
        'gasp.to', 'gasp.to.rst', 'gasp.to.shp',
        # ******************************************************************** #
        'gasp.web',
        'gasp.web.geosrv', 'gasp.web.geosrv.styl', 'gasp.web.geosrv.styl.sld',
        # ******************************************************************** #
        'gasp.cpu',
        'gasp.cpu.grs', 'gasp.cpu.grs.mng', 'gasp.cpu.grs.spanlst',
    ],
    #install_requires=[
        #'six==1.12.0', 'click==7.0', 'click-plugins==1.1.1',
        #'cligj==0.5.0', 'munch==2.3.2',
        #'psycopg2-binary==2.8.3', 'sqlalchemy==1.3.5', 'geoalchemy2==0.6.3',
        #'numpy==1.16.4',
        #'shapely==1.6.4', 'fiona==1.8.6', 'pyproj==2.2.1',
        #'pandas==0.24.1', 'geopandas==0.4.0',
        #'xlrd==1.2.0', 'xlwt==1.3.0', 'xlsxwriter==1.1.8',
        #'pyexcel_ods==0.5.6','dbf==0.98.0',
        #'bs4==0.0.1',
        #'netCDF4==1.5.1', 'polyline==1.4.0',
        #'flickrapi==2.4.0', 'tweepy==3.7.0',
        #'google-api-python-client==1.7.9',
        #'jupyter'
    #],
    include_package_data=True
)
