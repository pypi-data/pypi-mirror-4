# -*- coding: utf-8 -*
from rtree import index
from django.contrib.gis.gdal import DataSource
from shapefile import ShapefileReader


class GeodjangoShapefileReader(ShapefileReader):
    """Geodjango wrapper around a shapefile."""
    def open_datasource(self, filepath, layer):
        self.filepath = filepath
        ds = DataSource(self.filepath)
        return ds, ds[layer]

    def default_fieldname(self):
        return self.layer.fields[0]

    def get_feature_tuple(self, feat):
        return (feat.fid, feat.geom.envelope.tuple)

    def get_feature_by_id(self, i):
        # Can't assume that feature IDs are contiguous
        # if not hasattr(self, "feature_id_dict"):
        #     self.feature_id_dict = dict([(f.fid, i) for i, f in \
        #         enumerate(self.layer)])
        # return self.layer[self.feature_id_dict[i]]
        return self.layer[i]

    def reset_layer(self):
        pass

    def intersects(self, geom, excluded=None):
        """Find features in the shapefile that intersect the given geom."""
        if not excluded:
            excluded = ()
        in_index = self.index.intersection(geom.envelope.tuple)
        return [i for i in in_index if self.layer[i 
            ].geom.intersects(geom) and i not in excluded]

    def get_field_tuple(self, f):
        return (f.fid, float(f.get(self.amount_field)))

    def __iter__(self):
        return self.layer.__iter__()

