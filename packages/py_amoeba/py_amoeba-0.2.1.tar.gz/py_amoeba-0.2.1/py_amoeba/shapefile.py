# -*- coding: utf-8 -*
import os
from rtree import index
from osgeo import ogr, osr

def have_geos():
    pnt1 = ogr.CreateGeometryFromWkt( 'POINT(10 20)' )
    pnt2 = ogr.CreateGeometryFromWkt( 'POINT(30 20)' )
    try:
        result = pnt1.Union( pnt2 )
    except:
        result = None
    pnt1.Destroy()
    pnt2.Destroy()
    return bool(result)


class ShapefileReader(object):
    """Wrapper around a shapefile to provide a nicer interface."""
    def __init__(self, filepath, layer=0, amount_field=None):
        self.datasource, self.layer = self.open_datasource(filepath, layer)
        self.amount_field = amount_field or self.default_fieldname()

    def open_datasource(self, filepath, layer):
        assert have_geos(), "GEOS must be installed!"
        ds = ogr.Open(filepath)
        return ds, ds.GetLayerByIndex(layer)

    def default_fieldname(self):
        return self.layer.schema[0].GetName()

    def envelope_to_bounding_box(self, env):
        """Transform GDAL envelope to RTree bounding box"""
        # Envelope is xmin, xmax, ymin, ymax
        # RTree wants xmin, ymin, xmax, ymax
        assert len(env) == 4
        return (env[0], env[2], env[1], env[3])

    def reset_layer(self):
        self.layer.ResetReading()

    def get_feature_by_id(self, i):
        return self.layer.GetFeature(i)

    def create_spatial_index(self):
        """Create and populate r-tree spatial index."""
        self.index = index.Index()
        self.reset_layer()
        for feat in self.layer:
            self.index.add(*self.get_feature_tuple(feat))

    def get_feature_tuple(self, feat):
        return (feat.GetFID(), self.envelope_to_bounding_box( 
            feat.geometry().GetEnvelope()))

    def intersects(self, geom, excluded=None):
        """Find features in the shapefile that intersect the given geom."""
        if not excluded:
            excluded = ()
        in_index = self.index.intersection(self.envelope_to_bounding_box( 
            geom.GetEnvelope()))
        # GEOS is needed for Intersects to be correct - otherwise it is just
        # a bounding box call?!
        return [i for i in in_index if self.layer.GetFeature(i).geometry( 
            ).Intersects(geom) and i not in excluded]

    def get_field_tuple(self, f):
        return (f.GetFID(), f.GetFieldAsDouble(self.amount_field))

    def mapping_dict(self):
        """Create a dictionary mapping feature indices to amounts/weights"""
        self.reset_layer()
        self.mapping = dict([self.get_field_tuple(f) for f in self.layer])
        return self.mapping

    def __len__(self):
        return len(self.layer)

    def __iter__(self):
        self.reset_layer()
        return iter(self.layer)


class ShapefileWriter(object):
    def __init__(self, filename, geo, layer="geom", geom_type=None, **kwargs):
        assert has_geos, "GEOS must be installed!"
        self.filename = filename + ".shp"
        self.fields = {}
        self.create_file()
        # Infer geometry type from example geo
        if hasattr(geo, "geom_type"):
            geom_type = getattr(ogr, "wkb%s" % geo.geom_type)
        elif geom_type:
            pass
        else:
            raise ValueError, "Couldn't determine geometry type"
        self.layer = self.ds.CreateLayer(layer, geom_type=geom_type)
        for key, value in kwargs.iteritems():
            self.create_field(key, value)
        self.sr = osr.SpatialReference()
        self.sr.ImportFromWkt(geo.srs.wkt)
        self.feature_def = self.layer.GetLayerDefn()

    def create_file(self):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(self.filename):
            driver.DeleteDataSource(self.filename)
        self.ds = driver.CreateDataSource(self.filename)

    def create_field(self, name, kind):
        assert name not in self.fields
        if kind == int:
            self.fields[name] = ogr.FieldDefn(name, ogr.OFTInteger)
        elif kind == float:
            self.fields[name] = ogr.FieldDefn(name, ogr.OFTReal)
            self.fields[name].SetWidth(14)
            self.fields[name].SetPrecision(6)
        elif kind == str:
            self.fields[name] = ogr.FieldDefn(name, ogr.OFTString)
        self.layer.CreateField(self.fields[name])

    def add_record(self, obj, **kwargs):
        feature = ogr.Feature(self.feature_def)
        ogr_geo = ogr.CreateGeometryFromWkt(obj.wkt)
        ogr_geo.AssignSpatialReference(self.sr)
        feature.SetGeometry(ogr_geo)
        for key, value in kwargs.iteritems():
            feature.SetField(key, value)
        self.layer.CreateFeature(feature)
        feature.Destroy()

    def close(self):
        # Flush to file
        self.ds.Destroy()
        self.ds = None

