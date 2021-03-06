# -*- coding: utf-8 -*-
"""Visualize."""

from abc import ABC

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set()


class AbstractVisualization(ABC):

    def __init__(self, data, font_size=18):
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

    available_types = ["bar", "pie", "stacked-bar", "boxplot"]

    def __init__(self, data, var, plot_type, **kwargs):
        super().__init__(data)
        self.var = var
        self.plot_type = plot_type
        self.max_class = kwargs.pop('max_class', 10)

    @property
    def plot_type(self):
        return self._plot_type

    @plot_type.setter
    def plot_type(self, plot_type):
        if plot_type not in self.available_types:
            raise ValueError("You must specify a type "
                             f"in {self.available_types}")
        self._plot_type = plot_type

    @property
    def data_for_plot(self):
        data = self.data[self.var].value_counts()
        data.sort_values()
        if self.max_class > data.shape[0]:
            raise ValueError("Max class should be lower or equal to the number"
                             " of categories available in the categ variable.")
        x = data.index.values[:self.max_class]
        y = data.iloc[:self.max_class].values
        others = data.iloc[self.max_class:].sum()
        return list(x), list(y), others

    def pie(self, **kwargs):
        val = self.data[self.var].value_counts().sort_index()
        plt.figure(figsize=kwargs.get('figsize', (5, 6)))
        plt.pie(val, labels=val.index.str.upper(), **kwargs)
        plt.axis('equal')

    def bar(self, **kwargs):
        xlabel, ylabel = kwargs.pop('xlabel', ''), kwargs.pop('ylabel', '')
        x, y, others = self.data_for_plot
        if kwargs.pop('others_cat', True):
            x = np.append(x, ['others'])
            y = np.append(y, [others])

        if kwargs.get('orient', 'v') == 'h':
            x, y = y, x

        xticks_rotation = kwargs.pop('xticks_rotation', 0)
        plt.figure(figsize=kwargs.pop('figsize', (12, 8)))
        sns.barplot(x=x, y=y, **kwargs)
        plt.xticks(rotation=xticks_rotation)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    def stacked_bar(self, hue, **kwargs):
        data = self.data.copy()
        count = data[self.var].value_counts().sort_values(ascending=False)
        top_recurent = count.iloc[:self.max_class].index.values
        colors = kwargs.pop('colors', None)
        xlabel, ylabel = kwargs.pop('xlabel', ''), kwargs.pop('ylabel', '')
        xticks_rotation = kwargs.pop('xticks_rotation', 0)
        orient = kwargs.pop('orient', 'h')

        def labelizer(x):
            return x if x in top_recurent else 'other'

        data[self.var] = data[self.var].apply(labelizer)
        data = data.groupby([self.var, 'nutriscore_grade'])\
            .size().reset_index()\
            .pivot(columns=self.var, index='nutriscore_grade', values=0)

        if kwargs.pop('frequency', False):
            data = data / data.sum() * 100

        if not kwargs.pop('others_cat', True):
            try:
                data.drop('other', axis=1, inplace=True)
            except KeyError:
                pass

        if kwargs.pop('sort', 'values') == 'labels':
            sorted_labels = data.columns\
                            .sort_values(
                                ascending=kwargs.pop('ascending', True)).values
        else:
            sorted_labels = data.sum()\
                .sort_values(
                    ascending=kwargs.pop('ascending', True)).index.values

        data = data[sorted_labels]  # sort columns
        cumsum = data.cumsum()
        labels = data.columns.values

        plt.figure(figsize=kwargs.pop('figsize', (12, 8)))

        for i, label in enumerate(data.index.values):
            heights = data.loc[label]
            color = colors[i] if colors else None
            label_str = label.upper()
            if i > 0:
                if orient == 'h':
                    plt.barh(labels, heights,
                             left=cumsum.loc[data.index.values[i - 1]],
                             color=color, label=label_str)
                else:
                    plt.bar(labels, heights,
                            bottom=cumsum.loc[data.index.values[i - 1]],
                            color=color, label=label_str)
            else:
                if orient == 'h':
                    plt.barh(labels, heights,
                             color=color, label=label_str)
                else:
                    plt.bar(labels, heights,
                            color=color, label=label_str)

        plt.xticks(rotation=xticks_rotation)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.legend()

    def boxplot(self, **kwargs):
        fig, ax = plt.subplots(1, figsize=kwargs.pop('figsize', (12, 8)))
        sns.catplot(x=kwargs.pop('hue'), y=self.var,
                    kind="box", data=self.data, ax=ax, **kwargs)
        plt.close(2)

    def plot(self, **kwargs):
        if self.plot_type == 'bar':
            self.bar(**kwargs)

        elif self.plot_type == 'pie':
            self.pie(**kwargs)

        elif self.plot_type == 'stacked-bar':
            return self.stacked_bar(kwargs.pop('hue', None), **kwargs)

        elif self.plot_type == 'boxplot':
            return self.boxplot(**kwargs)
