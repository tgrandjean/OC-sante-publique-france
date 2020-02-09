# -*- coding: utf-8 -*-
"""parsers.

All parsers needed for string treatment are stored in this file.

"""
from abc import ABC, abstractclassmethod
import re

import unicodedata


mapper = {"grammes": "g",
          "gramme": "g",
          "g e": "g",
          "gr": "g",
          "grs": "g",
          "g egoutte": "g",
          "g egouttes": "g",
          "g net": "g",
          "gr.": "g",
          "gr": "g",
          "g net egoutte": "g",
          "g poids net egoutte": "g",
          "g minimum": "g",
          "ge": "g",
          "g poids net": "g",
          "g total": "g",
          "g poids net total": "g",
          "g.": "g",
          "g .": "g",
          ".gr": "g",
          "gram": 'g',
          "gramm": "g",
          "g net total": "g",
          "g e egoutte": "g",
          "g env.": "g",
          "grams": "g",
          "g environ": "g",
          "kg e": "kg",
          "kg.": "kg",
          "kg environ": "kg",
          "kg egoutte": "kg",
          "kgs": "kg",
          "kilos": "kg",
          "litres": "l",
          "litre": "l",
          "liter": "l",
          "ls": "l",
          "l e": "l",
          "l.": "l",
          "l.e": "l",
          "lt": "l",
          "cl e": "cl",
          "cl.": "cl",
          "cl e": "cl",
          "ml e": "ml",
          "ml.": "ml",
          }

NORMAL_UNITS = ['g', 'kg', 'l', 'ml', 'cl']


class Parser(ABC):
    """AbstractParser.

    Parsers should inherit from this class.
    For each parser, you have to override cls.formats and action method.
    """
    formats = list()

    @classmethod
    def match_regex(cls, string):
        """extract data from string using format's regex.

        :args::
            string (str) : string that you want extract data.
        :returns::
            match (re.match) : regular expression match.
        :raise::
            ValueError if no match detected.
        """
        for format in cls.formats:
            match = re.match(format, string)
            if match:
                return match
        raise ValueError('Unknown format')

    @classmethod
    def parse(cls, string):
        """execute action on the regex match.

        :args:
            string (str) : string that you want extract data.
        :returns:
            cls.action : execute action method if there is a match.
        :raise:
            ValueError if no match detected.
        """
        try:
            return cls.action(cls.match_regex(string))
        except ValueError as e:
            raise e

    @classmethod
    def ensure_std_unit(cls, unit):
        """use this method to standardize extracted units.

        :args:
            unit (str) : raw extracted unit.
        :returns:
            unit (str) : standard unit or raw unit otherwise.
        :usage:
            >>> Parser.ensure_std_unit('grammes')
                'g'
        """
        unit = unit.strip()
        return unit if not mapper.get(unit) else mapper.get(unit)

    @abstractclassmethod
    def action(cls, match):
        """Override this method to decide what to do with re.match"""
        pass


class SimpleParser(Parser):
    """Extract the quantity as float and the unit as str.

    :usage:
        >>> SimpleParser.parse('100g')
            (100.0, 'g')
        >>> SimpleParser.parse('2x100g')
            (200.0, 'g')
        >>> SimpleParser.parse('hello')
             ValueError                       Traceback (most recent call last)
             ...
    """

    formats = [re.compile(r'^(\d+[,\.]?\d*)[\s*]?([a-z\s\.]+)$'),
               re.compile(r'^(\d+)\s*[x\*]{1}\s*(\d+[\.,]?\d*)([a-z\s\.]+)$')]

    @classmethod
    def action(cls, match):
        if len(match.groups()) == 2:
            # ex 100 g
            value = float(match.group(1).replace(',', '.'))
            unit = match.group(2)
        elif len(match.groups()) == 3:
            # ex 2 x 100 g
            value = int(match.group(1)) * float(match.group(2).replace(',',
                                                                       '.'))
            unit = match.group(3)
        return value, cls.ensure_std_unit(unit)


class ComplexeParser(Parser):
    """Extract the quantity as float and the unit as str.

    :usage:
        >>> ComplexeParser.parse('100 g (2 x 50g)')
            (100, 'g')
    """
    formats = [re.compile(r'^(.+)\s*\((.+)\)$'),
               re.compile(r'^(.*),(.*)$')]

    @classmethod
    def choose_group(cls, groups):
        """Because there is two groups, we have to choose one and only one.

        If the two are equals there is no problem, but if they are different,
        we have to choose the best option. If we can't choose, example
        the first group returns 100 g and the second one returns 120 g, we
        raise a ValueError.
        """
        for group in groups:
            group[1] = cls.ensure_std_unit(group[1])

        if len(groups) == 1:
            # Only one group match
            return groups[0]
        else:
            if groups[0][1] == groups[1][1]:
                # same unit
                if groups[0][0] == groups[1][0]:
                    # same value
                    return groups[0]
                else:
                    # different values for the same unit
                    raise ValueError("Can't choose between values.")
            else:
                # different units
                if groups[0][1] in NORMAL_UNITS:
                    # the first group use regular unit
                    return groups[0]
                elif groups[1][1] in NORMAL_UNITS:
                    # the second group use regular unit
                    return groups[1]
                else:
                    # no standard unit detected in both groups
                    raise ValueError('Unknown units')

    @classmethod
    def action(cls, match):
        groups = list()
        for group in match.groups():
            try:
                groups.append(list(SimpleParser.parse(group.strip())))
            except ValueError:
                pass
        return cls.choose_group(groups)


class UnitParser(object):
    """UnitParser

    wrapper for quantity and unit treatment.

    :usage:
        >>> UnitParser.parse('100g')
            (100, 'g')
    """

    @classmethod
    def parse(cls, text):
        try:
            return cls.ensure_correct_unit(SimpleParser.parse(text))
        except ValueError:
            try:
                return cls.ensure_correct_unit(ComplexeParser.parse(text))
            except Exception:
                return 'Unknown frmt'

    @classmethod
    def ensure_correct_unit(cls, qty_tuple):
        """Check  if the returned unit is a normal unit for food or drink.

        :args:
            qty_tuple (tuple) : tuple contening the quantity (float)
                                and unit (str)
        :return:
            qty_tuple (tuple) : same as input

        :raise:
            ValueError if unit not in the NORMAL_UNITS.
        """
        if qty_tuple[1] not in NORMAL_UNITS:
            raise ValueError('Unknown unit')
        else:
            return qty_tuple

    @classmethod
    def normalize_string(cls, string):
        """Remove non ascii characters in a string.

        :usage:
            >>> UnitParser.normalize_string("éèàâêîôûç")
                'eeaaeiouc'
        """
        string = unicodedata.normalize('NFD', string)
        string = string.encode('ascii', 'ignore')
        string = string.decode("utf-8")
        return string.strip().lower()


# __all__ = ['UnitParser']
