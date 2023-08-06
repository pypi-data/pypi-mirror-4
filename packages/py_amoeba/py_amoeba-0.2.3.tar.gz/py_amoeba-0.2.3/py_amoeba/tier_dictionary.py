# -*- coding: utf-8 -*
from __future__ import division
from numpy import array
from scipy.stats import norm


def flatten(x):
    """Flattened a set of iterables into a single list.

    From http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks"""
    result = []
    for el in x:
        if hasattr(el, '__iter__') and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


class TierDictionary(object):
    """Data structure for storing AMOEBA ecotopes; keeps level and objects."""
    def __init__(self, obj_id, obj_weight, score):
        self.geo = {0: set([obj_id])}
        self.all_geo = set([obj_id])
        self.weights = {0: [obj_weight]}
        self.scores = {0: score}
        self.level = 0

    def __repr__(self):
        return "TierDictionary with levels/geos:\n%s" % self.geo

    def all_weights(self, max_level=1e12):
        return array(flatten([values for key, values in \
            self.weights.iteritems() if key <= max_level]))

    def add(self, objs, mapping, score):
        if set(objs).intersection(self.all_geo):
            # print set(objs).intersection(self.all_geo)
            raise ValueError
        self.level += 1
        self.geo[self.level] = set(objs)
        self.all_geo = self.all_geo.union(set(objs))
        self.weights[self.level] = [mapping[key] for key in objs]
        self.scores[self.level] = score

    @property
    def score(self):
        return self.scores[self.level]

    @property
    def normalized(self):
        """Return a dictionary with geo IDs as keys, and weights as values"""
        k_max = self.level
        if k_max == 0:
            return {}
        elif k_max == 1:
            # Only 1 for neighbors, not original element
            num_values = len(self.geo[1])
            return dict([(x, 1 / num_values) for x in self.geo[1]])
        else:
            res = {}
            denominator = norm.cdf(self.score) - norm.cdf(self.scores[0])
            for level in xrange(1, self.level + 1):
                numerator = norm.cdf(self.score) - norm.cdf(self.scores[
                    level])
                value = float(numerator / denominator)
                if value > 0:
                    res.update(dict([(key, value) for key in self.geo[
                        level]]))
            return res
