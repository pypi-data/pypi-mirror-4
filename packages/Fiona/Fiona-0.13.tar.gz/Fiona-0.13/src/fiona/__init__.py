# -*- coding: utf-8 -*-

"""
Fiona is OGR's neat, nimble, no-nonsense API.

Fiona provides a minimal, uncomplicated Python interface to the open
source GIS community's most trusted geodata access library and
integrates readily with other Python GIS packages such as pyproj, Rtree
and Shapely.

How minimal? Fiona can read features as mappings from shapefiles or
other GIS vector formats and write mappings as features to files using
the same formats. That's all. There aren't any feature or geometry
classes. Features and their geometries are just data.

A Fiona feature is a Python mapping inspired by the GeoJSON format. It
has `id`, 'geometry`, and `properties` keys. The value of `id` is
a string identifier unique within the feature's parent collection. The
`geometry` is another mapping with `type` and `coordinates` keys. The
`properties` of a feature is another mapping corresponding to its
attribute table. For example:

  {'id': '1',
   'geometry': {'type': 'Point', 'coordinates': (0.0, 0.0)},
   'properties': {'label': u'Null Island'} }

is a Fiona feature with a point geometry and one property. 

Features are read and written using objects returned by the
``collection`` function. These ``Collection`` objects are a lot like
Python ``file`` objects. A ``Collection`` opened in reading mode serves
as an iterator over features. One opened in a writing mode provides
a ``write`` method.

Usage
-----

Here's an example of reading a select few polygon features from
a shapefile and for each, picking off the first vertex of the exterior
ring of the polygon and using that as the point geometry for a new
feature writing to a "points.shp" file.

  >>> from fiona import collection
  >>> with collection("docs/data/test_uk.shp", "r") as inp:
  ...     output_schema = inp.schema.copy()
  ...     output_schema['geometry'] = 'Point'
  ...     with collection(
  ...             "points.shp", "w",
  ...             crs=inp.crs, 
  ...             driver="ESRI Shapefile", 
  ...             schema=output_schema
  ...             ) as out:
  ...         for f in inp.filter(
  ...                 bbox=(-5.0, 55.0, 0.0, 60.0)
  ...                 ):
  ...             value = f['geometry']['coordinates'][0][0]
  ...             f['geometry'] = {
  ...                 'type': 'Point', 'coordinates': value}
  ...             out.write(f)

Because Fiona collections are context managers, they are closed and (in
writing modes) flush contents to disk when their ``with`` blocks end.
"""

__all__ = []
__version__ = "0.13"

import os

from fiona.collection import Collection, supported_drivers


def open(path, mode='r', driver=None, schema=None, crs=None, encoding=None):
    
    """Open file at ``path`` in ``mode`` "r" (read), "a" (append), or
    "w" (write) and return a ``Collection`` object.
    
    In write mode, a driver name such as "ESRI Shapefile" or "GPX" (see
    OGR docs or ``ogr2ogr --help`` on the command line) and a schema
    mapping such as:
    
      {'geometry': 'Point', 'properties': { 'class': 'int', 'label':
      'str', 'value': 'float'}}
    
    must be provided. A coordinate reference system for collections in
    write mode can be defined by the ``crs`` parameter. It takes Proj4
    style mappings like
    
      {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84', 
       'no_defs': True}
    
    The drivers used by Fiona will try to detect the encoding of data
    files. If they fail, you may provide the proper ``encoding``, such as
    'Windows-1252' for the Natural Earth datasets.
    """
    if mode in ('a', 'r'):
        if not os.path.exists(path):
            raise IOError("no such file or directory: %r" % path)
        c = Collection(path, mode, encoding=encoding)
    elif mode == 'w':
        c = Collection(path, mode=mode, 
            crs=crs, driver=driver, schema=schema, 
            encoding=encoding)
    else:
        raise ValueError(
            "mode string must be one of 'r', 'w', or 'a', not %s" % mode)
    return c

collection = open

def prop_width(val):
    """Returns the width of a str type property.

    Undefined for non-str properties. Example:

      >>> prop_width('str:25')
      25
      >>> prop_width('str')
      80
    """
    if val.startswith('str'):
        return int((val.split(":")[1:] or ["80"])[0])
    return None
