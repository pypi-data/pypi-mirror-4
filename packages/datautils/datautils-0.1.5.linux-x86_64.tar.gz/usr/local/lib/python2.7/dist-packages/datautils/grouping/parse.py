#!/usr/bin/env python
"""
Data grouping routines
"""

import ast
import re

from discrete import DiscreteGroup
from continuous import ContinuousGroup


def parse_group(string):
    """
    Group definition syntax
    examples:
        'area' : discrete_group by area
        'dv[(0,10),(10, 20)]' : continuous_group by dv
    """
    m = re.match('([^[]+)([[].+[]])', string)
    if m is None:
        # assume a discrete_group
        return DiscreteGroup(string)
    else:
        g, l = m.groups()
        l = ast.literal_eval(l)
        return ContinuousGroup(g, l)
