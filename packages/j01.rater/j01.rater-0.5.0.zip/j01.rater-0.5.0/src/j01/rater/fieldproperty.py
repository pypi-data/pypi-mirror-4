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

_marker = object()


class RatingConverterFieldProperty(object):
    """RatingConverterFieldProperty with FiveStarRatingConverter as default
    
    This implementation requires a MongoSubItem class as instance and must
    provide a RatingConverter for the given field name in the converters dict.
    
    This field property is only responsible for to return a RatingConverter
    instance at any time. The real Rating items get stroed in such a
    RatingConverter instance. We never allow to replace an existing
    RatingConverter instance in the instance class dict.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__
        self.__field = field
        self.__ratingConverterFactory = field.ratingConverterFactory
        self.__name = name

    def __setUpRatingConverter(self, inst, value=None):
        # setup RatingConverter based on schema field factory
        converter = self.__ratingConverterFactory(value)
        inst.__dict__[self.__name] = converter
        converter.__parent__ = inst
        converter.__name__ = '%sRatingConverter' % self.__name
        return converter

    def __get__(self, inst, klass):
        if inst is None:
            return self
        converter = inst.__dict__.get(self.__name, _marker)
        if converter is _marker:
            # setup RatingConverter based on schema field factory with empty
            # value
            converter = self.__setUpRatingConverter(inst)
        return converter

    def __set__(self, inst, value):
        if inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'RatingFieldProperty is readonly')
        # we only allow to set an initial converter as value
        converter = self.__setUpRatingConverter(inst, value)
        # now validate
        field = self.__field.bind(inst)
        field.validate(converter)

    def __getattr__(self, name):
        return getattr(self.__field, name)
