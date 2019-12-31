"""univar

univariate analysis.

Thibault Grandjean
"""

import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tabulate import tabulate

class UnivariateAnalysis(object):
    """UnivariateAnalysis."""

    def __init__(self, dataframe):
        plt.rcdefaults()
        font = {'size'   : 16}
        sns.set()
        plt.rc('font', **font)
        self.data = dataframe

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, dataframe):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("You must pass a pandas's dataframe.")
        self._data = dataframe

    def completion_rate(self, column):
        """return completion rate for a column."""
        complete = self.data[column].dropna().shape[0] \
        / self.data[column].shape[0] * 100
        return f"completion rate -- {column} : {complete} %"

    def series_stats(self, column):
        """Return stats for a Series."""
        series = self.data[column]
        return [['mean', 'std', 'min', 'max'],
                [series.mean(), series.std(), series.min(), series.max()]]

    def graph_series(self, column):
        """Make a plot for a series."""
        if self.data[column].count() != self.data[column].shape[0]:
            warnings.warn('NaN detected in the series.'
            ' NaNs are not considered for calculation.')

        # Cut the window in 2 parts
        kwrgs = {"height_ratios": (.15, .85)}
        f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, figsize=(8, 8),
                                            gridspec_kw=kwrgs)

        # Add a graph in each part
        sns.boxplot(self.data[column].dropna(), ax=ax_box)
        sns.distplot(self.data[column].dropna(), ax=ax_hist)

        # Remove x axis name for the boxplot
        ax_box.set(xlabel='')
        plt.show()

    def make_analysis(self, column):
        """Make full analysis."""
        print(self.completion_rate(column))
        print(tabulate(self.series_stats(column), tablefmt="grid"))
        self.graph_series(column)
