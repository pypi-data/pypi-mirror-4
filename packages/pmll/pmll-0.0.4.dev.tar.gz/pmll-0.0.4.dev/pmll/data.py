# -*- coding: utf-8 -*-
from collections import namedtuple
import itertools
import numpy as np
from sympy import Symbol


__author__ = "Kirill Pavlov"
__email__ = "kirill.pavlov@phystech.edu"


class Feature(Symbol):
    """
    Feture representation, converts feature value according to one of the
    following types:

    nom: nominal value represented by string
    lin: float number in linear scale
    rank: float number, arithmetic operations are not supported
    bin: binary format, true/false or 1/0

    Feature does not know about data, does not have any mean or deviation.
    """
    DEFAULT_SCALE = "null"
    DEFAULT_TYPE = str
    FEATURE_TYPE_MAPPER = {
        "nom": str,
        "lin": float,
        "rank": float,
        "bin": bool,
    }

    def __init__(self, title, scale=None):
        self.title = unicode(title)
        self.scale = scale or self.DEFAULT_SCALE
        self.convert = self.FEATURE_TYPE_MAPPER.get(
            self.scale, self.DEFAULT_TYPE)

    def __new__(cls, title, **kwargs):
        title_str = unicode(title).encode('utf8')
        obj = super(cls, cls).__new__(cls, title_str, **kwargs)
        return obj

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self):
        return "%s:%s" % (unicode(self.title), unicode(self.scale))

    def __eq__(self, other):
        return self.title == other.title and self.scale == other.scale

    def __call__(self, obj):
        # for base features it is possible to get feature value from object
        # for complex features the same interface
        if self.is_Atom:
            value = getattr(obj, self.title, None)
            print "title: ", type(self.title), self.title, " value: ", value
            if value is not None:
                return self.convert(value)
            else:
                return None
        else:
            atoms = self.atoms(Feature)  # NOTE: dont use self.__class__
            atom_dict = {feature.title: feature for feature in atoms}

            subs = {
                feature_title: atom_dict[feature_title](feature_value)
                for feature_title, feature_value in obj._asdict().items()
                if feature_title in atom_dict
            }
            return self.evalf(subs=subs)


class Data(object):
    """
    Data is general data representation. It is object x feature matrix.
    There is no label, all of the features are equal. It is job for data
    manager to define what is label.
    """
    def __init__(self, objects, features=None):
        self.objects = np.matrix([list(obj) for obj in objects])
        self.features = features or [Feature("f%s" % i)
                                     for i in range(self.objects.shape[1])]


class DataReader(object):
    """
    Read data form tab separated file stream either into objects or matrix
    stream can be open(file) or line generator
    """
    @classmethod
    def __parse_header(cls, header):
        heared_prefix = "# "
        if not header.startswith(heared_prefix):
            msg = 'Bad header format. Should starts from "%s"' % heared_prefix
            raise ValueError(msg)
        else:
            header = header[len(heared_prefix):].split('#', 1)[0].rstrip()
            header = header.replace(",", "\t").replace(";", "\t")

        features = [
            Feature(*field.split(':'))
            for field in header.split("\t")
        ]

        duplicated_features = cls.__get_duplicated_features(features)
        if duplicated_features:
            msg = "Duplicated features passed: %s" % duplicated_features
            raise ValueError(msg)

        return features

    @classmethod
    def __get_duplicated_features(cls, features):
        """
        Return list of duplicated feature titles
        """
        feature_titles = [f.title for f in features]
        if len(set(feature_titles)) != len(features):
            return [f for f in feature_titles if feature_titles.count(f) > 1]

    @classmethod
    def read(cls, stream, delimiter="\t"):
        """
        Read tab separated values.
        Return features and object generator
        """
        # convert stream to generator
        stream = (line for line in stream)
        header = itertools.islice(stream, 1).next()
        features = cls.__parse_header(header)

        Object = namedtuple('Object', [f.title for f in features])
        objects = (Object(*[feature.convert(value) for feature, value
                            in zip(features, line.strip().split(delimiter))])
                   for line in stream)

        return objects, features
