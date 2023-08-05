# -*- coding: utf-8 -*
from __future__ import division
from numpy import *
from math import sqrt
import time
from tier_dictionary import TierDictionary
from shapefile import ShapefileReader


class NoNeighborsError(StandardError):
    pass


class AMOEBA(object):
    """
Calculates a spatial weights matrix using AMOEBA algorithm.

The basic algorithm is::

    for each geographic unit:
        neighbors = [original unit]
        calculate g_star of neigbors
        while True
            find all neighbors, excluding excluded neighbors
            find set of new neighbors that maximizes g_star
            if new g_star < old g_star
                break
            neighbors += new neighbors
            excluded += rejected neighbors

.. rubric:: Inputs

* obj: A shapefile or Django queryset of geography objects and weights.

Aldstadt, J. & Getis, A. (2006). Using AMOEBA to Create a Spatial Weights Matrix and Identify Spatial Clusters. Geographical Analysis, 38(4), 327--343. 
    """
    def __init__(self, ds, callback=None, *args, **kwargs):
        super(AMOEBA, self).__init__(*args, **kwargs)
        self.ds = self.get_ds(ds)
        self.callback = callback
        self.weights_dict = self.get_weights_dict()
        self.geo_ids = tuple(self.weights_dict.keys())
        self.number = float(len(self.geo_ids))
        values = array(self.weights_dict.values())
        self.average = float(average(values))
        self.pseudo_std = float(sqrt(
            (values ** 2).sum() / self.number - self.average ** 2)
            )

    def get_ds(self, ds):
        return ds

    def calculate(self, objs=None):
        objs = objs or self.ds

        results = {}
        count = len(objs)

        start_time = time.time()

        for index, obj in enumerate(objs):
            if not index % 50 and index > 0 and self.callback:
                # Send a progress message
                elapsed = time.time() - start_time
                eta = elapsed * (1 / (index / count) - 1)
                self.callback(eta=eta, progress=index, total=count,
                    elapsed=elapsed)

            oid = self.get_oid(obj)
            results[oid] = self.iterate(obj)

        return results

    def g_star(self, values_sum, values_num):
        """
Calculate g-star statistic for spatial unit in relation to neighbors.

The Gi* star statistic can be considered a standard normal variate.  So, the the cumulative probability of G*i(k_max) would be the cdf value for the standard normal distribution of the value G*i(k_max).  This value could be close to 1, but could also be much closer to zero in some cases.  So, using equation 2 of the AMOEBA paper, elements in the k_max level of contiguity would have zero weights with unit i.  These units are at the edge of the ecotope centered on i.  The units closer to i would have positive weights that increase as proximity to i increases. The value Gi*(0) is the Gi* value for the unit itself.
        """
        return (values_sum - self.average * values_num) / (
            self.pseudo_std * sqrt(
                (self.number - values_num) * values_num / (self.number - 1)
                )
            )

    def get_trend(self, obj, tiers):
        """Do a first round of expansion, and determine the trend direction"""
        neighbors = self.expand(tiers, set([0]))
        if not neighbors:
            raise NoNeighborsError

        # Create array with col 1: geo ids, col 2: weights
        data = array([self.weights_dict[key] for key in neighbors])
        # Sort by weight ascending
        data = data[argsort(data)]

        orig_value = float(sum(tiers.all_weights()))
        if tiers.score < 0:
            operator = max
        else:
            operator = min

        up_score = operator([self.g_star(float(data[:index].sum()) + \
            orig_value, index + 1) for index in range(1, data.shape[0] + 1)])
        down_score = operator([self.g_star(float(data[::-1][:index].sum()) + \
            orig_value, index + 1) for index in range(1, data.shape[0] + 1)])
        if tiers.score < 0:
            trend = "downwards" if (down_score < up_score) else "upwards"
        else:
            trend = "downwards" if (down_score > up_score) else "upwards"
        return trend

    def iterate(self, obj):
        oid = self.get_oid(obj)
        weight = self.weights_dict[oid]
        tiers = TierDictionary(oid, weight, self.g_star(weight, 1))
        excluded = set([0])

        try:
            trend = self.get_trend(obj, tiers)
        except NoNeighborsError:
            return tiers.normalized

        while True:
            neighbors = self.expand(tiers, excluded)
            if not neighbors:
                # No new neighbors found; stop iteration
                break

            # Create array with col 1: geo ids, col 2: weights
            data = hstack((array(neighbors).reshape((-1, 1)), array([
                self.weights_dict[key] for key in neighbors]).reshape((-1, 1)
                )))
            # Sort by weight
            if trend == "upwards":
                data = data[argsort(data[:, 1])]
            else:
                data = data[argsort(data[:, 1])[::-1]]

            already_values = tiers.all_weights()
            already_number = float(already_values.shape[0])
            already_sum = float(already_values.sum())
            base_score = loop_score = tiers.score
            new_neighbors = set()

            for index in range(1, data.shape[0]):
                values = data[:index, 1]

                new_score = self.g_star(float(values.sum()) + already_sum,
                    float(values.shape[0]) + already_number)

                if not (new_score > loop_score > 0 or new_score < \
                        loop_score < 0):
                    break
                else:
                    new_neighbors = set(unique(data[:index, 0].astype(int)
                        ).tolist())
                    loop_score = new_score

            if loop_score == base_score:
                # No better set of neighbors was found
                break
            else:
                # Add neighbors and set new high score
                excluded = excluded.union(set(neighbors).difference(
                    set(new_neighbors)))
                tiers.add(new_neighbors, self.weights_dict, loop_score)

        return tiers.normalized

    def get_oid(self, o):
        return o.id


class ShapefileAMOEBA(AMOEBA):
    """AMOEBA algorithm adapted to the objects defined by the Python GDAL OGR shapefile interface."""
    shapefile_reader = ShapefileReader

    def __init__(self, *args, **kwargs):
        super(ShapefileAMOEBA, self).__init__(*args, **kwargs)
        self.neighbor_cache = {}

    def get_ds(self, ds):
        if isinstance(ds, basestring):
            ds = self.shapefile_reader(ds)
            ds.create_spatial_index()
            return ds
        elif isinstance(ds, ShapefileReader):
            if not hasattr(ds, "index"):
                ds.create_spatial_index()
            return ds
        else:
            raise TypeError("Data source not understood")

    def get_neighbors(self, n):
        try:
            return self.neighbor_cache[n]
        except KeyError:
            feat = self.ds.get_feature_by_id(n)
            neighbors = self.ds.intersects(self.get_buffered_geom(feat),
                excluded=(n,))
            self.neighbor_cache[n] = neighbors
            return neighbors

    def expand(self, tiers, excluded):
        if tiers.level > 6:
            # One could continue to expand, but there is not really any
            # point; the spatial weights are quite small anyway.
            return []
        new_neighbors = reduce(
            set.union,
            [set(self.get_neighbors(x)) for x in tiers.geo[tiers.level]]
            )
        return list(new_neighbors.difference(excluded).difference(
            tiers.all_geo))

    def get_buffered_geom(self, feat):
        return feat.geometry().Buffer(0.01)

    def get_oid(self, o):
        return o.GetFID()

    # def write_to_shapefile(self, tiers, obj):
    #     """Write tiers to shapefile for inspection."""
    #     filename = self.ds.filepath.split("/")[-1].split(".")[0]
    #     sf = ShapefileWriter('amoeba-output-%s-%s' % (filename,
    #         self.get_oid(obj)), self.ds.layer[0].geom, "amoeba", id=int,
    #         weight=float, cf=float)
    #
    #     for key, weight in tiers.normalized.iteritems():
    #         obj = self.ds.layer[key]
    #         sf.add_record(obj.geom, id=key, weight=weight,
    #             cf=obj.get(self.ds.amount_field))
    #
    #     sf.close()

    def get_weights_dict(self):
        return self.ds.mapping_dict()
