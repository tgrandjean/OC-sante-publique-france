# -*- coding: utf-8 -*-
"""Visualize."""

from abc import ABC

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set()

class AbstractVisualization(ABC):

    def __init__(self, data, font_size=16):
        plt.rcdefaults()
        font = {"size": font_size}
        sns.set()
        plt.rc('font', **font)
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if type(data) != pd.DataFrame and type(data) != pd.Series:
            raise ValueError("You must pass a pandas.DataFrame or Series obj.")
        self._data = data


class DistributionPlot(AbstractVisualization):

    def __init__(self, data, var, **kwargs):
        super().__init__(data)
        self.var = var

    def plot(self):
        # Cut the window in 2 parts
        gridspec_kw = {"height_ratios": (.15, .85)}
        f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, figsize=(8, 8),
                                            gridspec_kw=gridspec_kw)

        # Add a graph in each part
        sns.boxplot(self.data[self.var].dropna(), ax=ax_box)
        sns.distplot(self.data[self.var].dropna(), ax=ax_hist)

        # Remove x axis name for the boxplot
        ax_box.set(xlabel='')


class RepartitionPlot(AbstractVisualization):

    available_types = ["bar", "pie"]

    def __init__(self, data, var, plot_type, **kwargs):
        super().__init__(data, **kwargs)
        self.var = var
        self.plot_type = plot_type
        self.max_class = kwargs.get('max_class', 10)

    @property
    def plot_type(self):
        return self._plot_type

    @plot_type.setter
    def plot_type(self, plot_type):
        if plot_type not in self.available_types:
            raise ValueError("You must specify a type "
                             f"in {self.available_types}")
        self._plot_type = plot_type

    def plot(self, **kwargs):
        if self.plot_type == 'bar':
            orient = kwargs.get('orient', 'v')
            data = self.data[self.var].value_counts()
            data.sort_values()
            x = data.iloc[:self.max_class].index.values
            y = data.iloc[:self.max_class].values
            others = data.iloc[self.max_class:].sum()
            x = np.append(x, ['others'])
            y = np.append(y, [others])
            if orient == 'h':
                x, y = y, x
            plt.figure(figsize=kwargs.get('figsize', (12, 8)))
            sns.barplot(x=x, y=y, **kwargs)
            plt.xlabel(kwargs.get("xlabel"))
            plt.ylabel(kwargs.get("ylabel"))
        elif self.plot_type == 'pie':
            val = self.data[self.var].value_counts().sort_index()
            plt.figure(figsize=kwargs.get('figsize', (5, 6)))
            plt.pie(val,
                    labels=val.index.str.upper(),
                    colors=kwargs.get('colors'),
                    explode=kwargs.get('explode'))
            plt.axis('equal')
