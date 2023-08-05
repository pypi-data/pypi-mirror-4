##############################################################################
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
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import decimal
import zope.interface
import zope.i18n
import zope.i18nmessageid
import zope.location.location

import m01.mongo.item
import m01.mongo.util
from m01.mongo.fieldproperty import MongoFieldProperty

from j01.rater import interfaces
from j01.rater import scoresystem

_ = zope.i18nmessageid.MessageFactory('p01')


# XXX: compute average on each new rating, use dict for dump data instead of list
class RatingConverter(zope.location.location.Location):
    """Rating converter implementation using pid as key and score key as value.
    
    Don't get confused we use in some methods key as name for the dict value
    because this value is the score key which get stored as value with the
    principal id as dict key.
    """

    zope.interface.implements(interfaces.IRatingConverter)

    # score system
    scoreSystem = None

    def __init__(self, data=None):
        self.data = {}
        if data is not None:
            # note we skip score from data dict, this is only used for 
            # render average/score in table data
            self._average = data.get('average', 0)
            for d in data.get('ratings'):
                # data is a list of dicts with pid and key values
                self.data[d['pid']] = d['key']
        else:
            self._average = 0

    def dump(self):
        """Dump Rating items to list."""
        return {'average': self.average,
                'max': self.maxScore,
                'ratings': [{'pid': pid, 'key': key}
                            for pid, key in self.data.items()]}

    def rate(self, pid, key):
        """See interfaces.IRatingConverter"""
        if not self.scoreSystem.isValidScore(key):
            raise ValueError('Invalid rating key %r' % key)

        if self.data.get(pid) == key:
            # do nothing if no change
            return False
        self.data[pid] = key
        # update average
        self.updateAverage()
        # mark parent as changed
        self.__parent__._m_changed = True
        return True

    def remove(self, pid):
        """See interfaces.IRatingConverter"""
        if pid not in self.data:
            return False
        del self.data[pid]
        # update average
        self.updateAverage()
        # mark parent as changed
        self.__parent__._m_changed = True
        return True

    def getRating(self, pid):
        """See interfaces.IRatingConverter"""
        if pid in self.data:
            value = self.data[pid]
        else:
            value = 0
        return float(value)

    def countRatings(self):
        """See interfaces.IRatingConverter"""
        return len(self.data)

    def countScores(self):
        """See interfaces.IRatingConverter"""
        key_count = {}
        for key in self.data.values():
            key_count.setdefault(key, 0)
            key_count[key] += 1

        return [(score, key_count.get(score.key, 0))
                for score in self.scoreSystem.scores]

    def updateAverage(self):
        total = sum([decimal.Decimal(key)
                    for key in self.data.values()])
        try:
            average = total/len(self.data)
        except ZeroDivisionError:
            average = 0
        self._average = float(average)

    @property
    def average(self):
        """See interfaces.IRatingConverter"""
        return self._average

    @property
    def scores(self):
        """See interfaces.IRatingConverter"""
        return self.scoreSystem.scores

    @property
    def maxScore(self):
        """See interfaces.IRatingConverter"""
        return self.scoreSystem.maxScore

    @property
    def scoreKeys(self):
        """See interfaces.IRatingConverter"""
        return self.scoreSystem.scoreKeys

    def getLabel(self, key):
        """See interfaces.IRatingConverter"""
        return self.scoreSystem.getLabel(key)

    def translate(self, key, domain=None, mapping=None, context=None,
        target_language=None, default=None):
        """See interfaces.IRatingConverter"""
        msgid = self.getLabel(key)
        return zope.i18n.translate(msgid, domain=domain, mapping=mapping,
            context=context, target_language=target_language, default=default)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.__parent__)


class FiveStarRatingConverter(RatingConverter):
    """FiveStarRatingConverter"""

    # score system
    scoreSystem = scoresystem.fiveStarScoreSystem


class FiveHalfStarRatingConverter(RatingConverter):
    """FiveHalfStarRatingConverter"""

    # score system
    scoreSystem = scoresystem.fiveHalfStarScoreSystem


class FiveHalfStarFullRatingConverter(RatingConverter):
    """FiveHalfStarFullRatingConverter"""

    # score system
    scoreSystem = scoresystem.fiveHalfStarFullScoreSystem

