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

import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.i18nmessageid
import zope.location.interfaces

from z3c.form.interfaces import ITextWidget

import m01.mongo.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


CANCEL_RATING_KEY = u'cancel'
CANCEL_RATING_LABEL = _(u'cancel')


class IScore(zope.interface.Interface):
    """The score."""

    key = zope.schema.TextLine(
        title=u'Score Key',
        description=u'The score key used for rate something.',
        required=True)

    value = zope.schema.Float(
        title=u'Score value',
        description=u'The score value as decimal.',
        required=True)

    label = zope.schema.TextLine(
        title=u'Score label',
        description=u'The score label use for represent the rating.',
        required=True)


class IScoreSystem(zope.interface.Interface):
    """The score system."""

    __name__ = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the score system.',
        required=True)

    scores = zope.schema.List(
            title = u'The scores',
            description = u"""
                A list containing tuples with (key, value, numerical).
                key is a string used for a simple access via JSON.
                value is the external repesentation as a i18n message.
                numerical is stored in the rating
                """,
            default = [],
            )

    maxScore = zope.schema.Float(
        title=u'Maximal score value',
        description=u'The maximal score value as float.',
        required=True)

    maxScoreLabel = zope.schema.TextLine(
        title=u'Maximal score label',
        description=u'The maximal score label.',
        required=True)

    def isValidScore(value):
        """Check if the value is a valid score for the scoring system.

        value must be a value from `scores`.
        """


class IRatingConverter(zope.location.interfaces.ILocation):
    """Stores rating score keys for principal id"""

    scoreSystem = zope.schema.Object(
        title=u'Score System',
        description=u'The score system used for rating.',
        schema=IScoreSystem,
        required=True)

    scores = zope.schema.List(
        title=u'Scores',
        description=u'The scores of the IScoreSystem.',
        value_type = zope.schema.Object(
            title=u'Score',
            description=u'Score object',
            schema=IScore,
            required=True),
        readonly=True)

    scoreKeys = zope.schema.List(
        title=u'Score Keys',
        description=u'List of score keys',
        value_type = zope.schema.TextLine(
            title=u'Score Key',
            description=u'Score key value',
            required=True),
        readonly=True)

    maxScore = zope.schema.Float(
        title=u'Maximal score value',
        description=u'The maximal score value as float.',
        required=True)

    average = zope.schema.Float(
        title=u'Average value',
        description=u'The average value as float.',
        readonly=True)

    def rate(pid, key):
        """Create a rating with score key for the principal id.

        This method should override existing ratings, if applicable.
        """

    def remove(pid):
        """Remove the rating for the given principal id.

        If no rating exists, do nothing and simply return.
        """

    def getRating(pid):
        """Get a rating for the given principal id.

        The result will be an ``IRating`` object. If no rating is found, rais
        a ``ValueError``.
        """

    def countRatings():
        """Counts the total ratings"""

    def countScores():
        """Count how many times each value was giving.

        The result will be a list of tuples of the type ``(score,
        amount)``. ``score`` is in turn a tuple of ``(name, value)``.
        """

    def getLabel(key):
        """Returns the label for the given rating key."""

    def translate(key, domain=None, mapping=None, context=None,
        target_language=None, default=None):
        """Can translate a i18n message id label by the given rating key."""


# schema
class IRatingField(zope.schema.interfaces.IField):
    """Five half star rater field."""


class IFiveStarRatingField(IRatingField):
    """Five half star rater field."""


class IFiveHalfStarRatingField(IRatingField):
    """Five half star rater field."""


class IFiveHalfStarFullRatingField(IRatingField):
    """Five half star full rater field."""


# widget
class IRatingWidget(ITextWidget):
    """Rating widget base interface."""

    isHalfStar = zope.schema.Field(u"is half star marker")
    averageStars = zope.schema.Field(u"Average stars HTML")
    ratableStars = zope.schema.Field(u"Ratable stars HTML")
    j01RaterId = zope.schema.Field(u"Rater element id")
    jsonRPCURL = zope.schema.Field(u"JSON-RPC URL")
    javaScript = zope.schema.Field(u"JavaScript")


class IFiveStarRatingWidget(IRatingWidget):
    """Five star rater widget."""


class IFiveHalfStarRatingWidget(IRatingWidget):
    """Five half star rater widget."""


class IFiveHalfStarFullRatingWidget(IRatingWidget):
    """Five half star full rater widget."""
