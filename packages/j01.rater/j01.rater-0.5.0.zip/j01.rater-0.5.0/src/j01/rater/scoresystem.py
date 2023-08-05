##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import decimal
import zope.interface
import zope.i18nmessageid

from j01.rater import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


class Score(object):
    """I18n aware score implementation"""

    zope.interface.implements(interfaces.IScore)

    def __init__(self, key, label):
        self.key = key
        self.value = float(key)
        self.label = label

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.key)


class ScoreSystem(object):
    """A score system defines the key and label.
    
    A key string is used for handling the requests.
    
    A key must be convertable to float for compute the average.
    
    A label is a i18n message id this is used for translations.
    """

    zope.interface.implements(interfaces.IScoreSystem)

    def __init__(self, name, scores):
        self.__name__ = name
        self.scores = scores
        self.scoreKeys = []
        self.scoreLabels = {}
        self.maxScore = 0
        self.maxScoreLabel = u''
        for score in self.scores:
            self.scoreLabels[score.key] = score.label
            self.scoreKeys.append(score.key)
            if score.value > self.maxScore:
                self.maxScore = score.value
                self.maxScoreLabel = score.label

    def getLabel(self, key):
        return self.scoreLabels[key]

    def isValidScore(self, key):
        return key in self.scoreKeys

    def __reduce__(self):
        return self.__name__


fiveStarScoreSystem = ScoreSystem(
    'FiveStarScoreSystem',
    [Score(u'1', _('fiveStarScoreSystem.crap')),
     Score(u'2', _('fiveStarScoreSystem.poor')),
     Score(u'3', _('fiveStarScoreSystem.okay')),
     Score(u'4', _('fiveStarScoreSystem.good')),
     Score(u'5', _('fiveStarScoreSystem.best')),
     ])


fiveHalfStarScoreSystem = ScoreSystem(
    'FiveHalfStarScoreSystem',
    [Score(u'0.5', _('fiveStarScoreSystem.0.5')),
     Score(u'1', _('fiveStarScoreSystem.1')),
     Score(u'1.5', _('fiveStarScoreSystem.1.5')),
     Score(u'2', _('fiveStarScoreSystem.2')),
     Score(u'2.5', _('fiveStarScoreSystem.2.5')),
     Score(u'3', _('fiveStarScoreSystem.3')),
     Score(u'3.5', _('fiveStarScoreSystem.3.5')),
     Score(u'4', _('fiveStarScoreSystem.4')),
     Score(u'4.5', _('fiveStarScoreSystem.4.5')),
     Score(u'5', _('fiveStarScoreSystem.5')),
     ])


fiveHalfStarFullScoreSystem = ScoreSystem(
    'FiveHalfStarFullScoreSystem',
    [Score(u'1', _('fiveHalfStarFullScoreSystem.1')),
     Score(u'2', _('fiveHalfStarFullScoreSystem.2')),
     Score(u'3', _('fiveHalfStarFullScoreSystem.3')),
     Score(u'4', _('fiveHalfStarFullScoreSystem.4')),
     Score(u'5', _('fiveHalfStarFullScoreSystem.5')),
     Score(u'6', _('fiveHalfStarFullScoreSystem.6')),
     Score(u'7', _('fiveHalfStarFullScoreSystem.7')),
     Score(u'8', _('fiveHalfStarFullScoreSystem.8')),
     Score(u'9', _('fiveHalfStarFullScoreSystem.9')),
     Score(u'10', _('fiveHalfStarFullScoreSystem.10')),
     ])

