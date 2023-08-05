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

import zope.interface
import zope.schema
from zope.schema.interfaces import SchemaNotProvided

from j01.rater import interfaces
from j01.rater.rating import FiveStarRatingConverter
from j01.rater.rating import FiveHalfStarRatingConverter
from j01.rater.rating import FiveHalfStarFullRatingConverter


class RatingField(zope.schema.Field):
    """Rating manager field."""

    zope.interface.implements(interfaces.IRatingField)

    ratingConverterFactory = None

    def _validate(self, value):
        # schema has to be provided by value
        if not interfaces.IRatingConverter.providedBy(value):
            raise SchemaNotProvided



class FiveStarRatingField(RatingField):
    """Five half star score system rating field."""

    ratingConverterFactory = FiveStarRatingConverter

    zope.interface.implements(interfaces.IFiveStarRatingField)


class FiveHalfStarRatingField(RatingField):
    """Five half star score system rating field."""

    ratingConverterFactory = FiveHalfStarRatingConverter

    zope.interface.implements(interfaces.IFiveHalfStarRatingField)


class FiveHalfStarFullRatingField(RatingField):
    """Five half star score system rating field with 1-10 ratings."""

    ratingConverterFactory = FiveHalfStarFullRatingConverter

    zope.interface.implements(interfaces.IFiveHalfStarFullRatingField)
