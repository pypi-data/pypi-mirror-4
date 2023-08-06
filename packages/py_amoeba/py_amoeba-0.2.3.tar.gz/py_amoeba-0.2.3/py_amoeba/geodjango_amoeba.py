# -*- coding: utf-8 -*
from __future__ import division
from django.contrib.gis.geos import fromstr
from django.contrib.gis.gdal import OGRGeometry
from amoeba import ShapefileAMOEBA
from geodjango_shapefile import GeodjangoShapefileReader


class GeodjangoShapefileAMOEBA(ShapefileAMOEBA):
    """Use Django bindings instead of OGR bindings, as they don't segfault every 10 seconds."""
    shapefile_reader = GeodjangoShapefileReader

    def get_buffered_geom(self, feat):
        return OGRGeometry(fromstr(feat.geom.wkt).buffer(0.01).wkt)

    def get_oid(self, o):
        return o.fid

