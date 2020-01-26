"""string_handler.

Adapted from https://github.com/OpenRefine/OpenRefine/wiki/Clustering-In-Depth

This module contains a collection of clustering methods for strings
refinement.

Note : The project OpenRefine is under BSD-3-Clause so check the license
https://github.com/OpenRefine/OpenRefine/blob/master/LICENSE.txt

"""

from abc import ABC, abstractclassmethod
import string

import pandas as pd
import unicodedata
from tqdm import tqdm

tqdm.pandas()


class Keyer(ABC):
    """Keyer abstract class.

    Parent class for fingerprint needed for "collision methods"

    """

    @classmethod
    def preprocess_string(cls, s):
        """Preprocess string.

        Strip, lowerise and remove punctuation in a string.

        Args:
            s (str) : string to process

        Return:
            s (str) : processed string

        Example:
            s = "   Hello ! Héhé this is    a shitty example !!!"
            >>>Keyer.preprocess_string(s)
            'hello hehe this is a shitty example'

        """
        s = s.strip()  # first remove whitespace around the string
        s = s.lower()  # then lowercase it
        # then replace all punctuation and control chars by spaces
        # we need to keep spaces for now otherwise:
        # Carrefour,Carrefour-baby --> CarrefourCarrefourbaby instead of
        # Carrefour, Carrefour-baby --> Carrefour Carrefour baby
        # The translator map all punctation symbole with whitespace
        translator = str.maketrans(string.punctuation,
                                   ' ' * len(string.punctuation))
        # make the translation, all punctation became a space
        s = s.translate(translator)
        # then split on whithespaces
        frags = s.split(' ')
        # drop trailing whitespaces
        # the split on whitespaces give you a list with empty strings
        # so drop them
        frags = [x for x in frags if x]
        # join all fragments back together
        s = ' '.join(frags)

        # replace non ascii chars
        s = cls.asciify(s)
        return s

    @classmethod
    def asciify(cls, s):
        """Replace all no ascii characters in a string.

        Args:
            s (str) : string to process

        Return:
            s (str) : processed string

        Example:
            >>>Keyer.asciify("é")
            'e'
        """
        s = unicodedata.normalize('NFD', s)
        s = s.encode('ascii', 'ignore')
        s = s.decode('utf-8')
        return s

    @abstractclassmethod
    def key(cls, s):
        """Override this class method."""
        msg = 'This method should be overriden in child class'
        raise NotImplementedError(msg)


class StringFingerPrint(Keyer):
    """Get finger print of a string.

    create a fingerprint of a string: after preprocessing, we split on
    whitespaces then we sort fragments of the string and then we join all
    fragments back together with whitespaces between each fragments.

    Example:
        >>>StringFingerPrint.key('Hello this is a shitty example.')
        'a example hello is shitty this'
    """

    @classmethod
    def key(cls, s):
        """Create a StringFingerPrint from a string. See class docs."""
        s = cls.preprocess_string(s)
        # split string on white spaces
        frags = s.split(' ')
        # sort fragments by alphabetical order
        frags.sort()
        # remove whitespace around fragments
        frags = list(map(str.strip, frags))
        # remove duplicated fragments
        frags = list(dict.fromkeys(frags))
        # join ordered fragments back together
        s = " ".join(frags)
        return s.strip()


class NGramFingerPrint(Keyer):
    """Get NGram finger print from a string.

    create a fingerprint of a string: after preprocessing, we remove all
    whitespaces and we create a list of n-grams of the string. Once we have
    all n-grams from the string, we sort them and then we join them back
    together.

    Args:
        s (str) : the string that you want a fingerprint.
        ngram_size (int) : the size of n-grams (default: 2)

    Example:
        >>>NGramFingerPrint.key('Hello this is a shitty example.',
                                ngram_size=2)
        'amaselexhehiisitlelllompotplsashsithtttyxaye'
    """

    @classmethod
    def key(cls, s, ngram_size=2):
        """Create a NGramFingerPrint from a string. See class docs."""
        s = cls.preprocess_string(s)
        # remove whitespace
        s = s.replace(' ', '')
        # get fragments
        frags = [x for x in cls.ngram_split(s, ngram_size)]
        # order fragments
        frags.sort()
        # remove duplicated fragments
        frags = list(dict.fromkeys(frags))
        # join ordered fragments back
        s = "".join(frags)
        return s

    @classmethod
    def ngram_split(cls, s, ngram_size):
        """ngram_split : yield all ngrams from a string.

        Args:
        """
        for i in range(len(s) - ngram_size + 1):
            yield s[i:i + ngram_size]


class StringClustering(object):
    """StringClustering.

    Create cluster of string following different methods.

    """

    methods = [
        'StringFingerPrint',
        'NGramFingerPrint'
    ]

    def __init__(self, series, method="StringFingerPrint", **kwargs):
        self.series = series
        self.original_name = 'original_strings'
        self.series.name = self.original_name
        self.method = method
        self._data = pd.DataFrame(series)
        self._orphans = None
        self._clusters = None
        self.kwargs = kwargs

    @property
    def series(self):
        return self._series

    @series.setter
    def series(self, series):
        if type(series) != pd.Series:
            raise ValueError('You must pass a pandas.Series object.')
        self._series = series

    @property
    def method(self):
        return self._method.split('.')[0]

    @method.setter
    def method(self, method):
        if method not in self.methods:
            raise ValueError("You must specify a method available in :\n",
                             self.methods)
        self._method = method + ".key"

    @property
    def keys(self):
        try:
            self._data['key']
        except KeyError:
            self.compute_keys()
        return self._data['key']

    def compute_keys(self):
        self._data['key'] = self._data[self.original_name]\
            .apply(eval(self._method), **self.kwargs)

    @property
    def orphans(self):
        if type(self._orphans) != pd.Series:
            keys = self.keys
            count = keys.value_counts()
            self._orphans = count[count == 1]
        return self._orphans

    @property
    def clusters(self):
        if type(self._clusters) != pd.Series:
            keys = self.keys
            count = keys.value_counts()
            self._clusters = count[count > 1]
        return self._clusters

    def get_cluster_name(self, key):
        original_names = self._data[self.keys == key]
        original_names = original_names[self.original_name].value_counts()
        return original_names.idxmax()

    def mapper(self):
        mapp = dict()
        for cluster in tqdm(self.clusters.index):
            mapp[cluster] = self.get_cluster_name(cluster)
        return lambda x: mapp[x]

    def get_results(self):
        self.clustering_result()
        print("Create a mapper function this can take a while.")
        mapper = self.mapper()
        data = self._data.set_index(self._data['key'])
        data.loc[self.orphans.index, "key"] = data.loc[self.orphans.index,
                                                       self.original_name]
        print("Replace fingerprint by original name.")
        data.loc[self.clusters.index, "key"] =\
            data.loc[self.clusters.index, "key"].progress_apply(mapper)
        return data["key"]

    def clustering_result(self):
        origin_class = self._data[self.original_name].drop_duplicates().count()
        n_clusters = self.clusters.count()
        n_orphans = self.orphans.count()
        n_classes = self.keys.drop_duplicates().count()
        print(f'Detected {n_clusters} clusters with {self.method} \n',
              f'Total classes detected {n_classes}.\n',
              f'Original dataset contains {origin_class} classes\n',
              f'There is {n_orphans} orphans.')
