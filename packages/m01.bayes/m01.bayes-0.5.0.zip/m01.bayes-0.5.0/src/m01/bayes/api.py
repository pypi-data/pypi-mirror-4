###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Bayesian API

"""

# guess helper
def guessBayes(bayes, tokens, minRatio=0.9, maxValues=1):
    # skip if no maxValue is given
    if not maxValues:
        return None
    # skip if no ratio is given
    if not minRatio:
        if maxValues == 1:
            return None
        else:
            return []
    data = bayes.guess(tokens)
    # handel single value
    if maxValues == 1:
        for word, ratio in data:
            if ratio >= minRatio:
                return word, ratio
        return None

    # handle mutliple values
    counter = 0
    res = []
    append = res.append
    for word, ratio in data:
        if counter >= maxValues:
            break
        if ratio >= minRatio:
            append((word, ratio))
        counter += 1
    return res


def guessBayesValue(bayes, tokens, minRatio=0.9, maxValues=1):
    data = guessBayes(bayes, tokens, minRatio, maxValues)
    if not data:
        return data
    # handel single value
    if maxValues == 1:
        return data[0]
    return [word for word, ratio in data]
