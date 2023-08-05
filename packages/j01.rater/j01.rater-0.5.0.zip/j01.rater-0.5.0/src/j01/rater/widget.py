##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: __init__.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""

from xml.sax.saxutils import quoteattr

import zope.interface
import zope.component
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.authentication.interfaces import IUnauthenticatedPrincipal

import z3c.form.interfaces
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import IDataConverter
from z3c.form.widget import FieldWidget
from z3c.form.browser.text import TextWidget

from j01.rater import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


j01_rater_template = """
<script type="text/javascript">
  $("#%s").j01Rater({%s
  });
</script>
"""


class RatingWidget(TextWidget):
    """Rating widget for single rating
    
    The widget does not render input HTML elements e.g. radio. This means the
    widget will not support any usefull value for z3c.form if we extract the
    widget value. The widget just returns NO_VALUE and the field property
    called RatingConverterFieldProperty prevents to store None as value.

    We could probably later implement radio input and support storing such
    radio input based rating values.

    """

    zope.interface.implementsOnly(interfaces.IRatingWidget)

    css = u'j01-rater'

    # internal handler
    _leftStarFlag = True
    converter = None
    scores = []
    average = 0
    current = 0
    maxScore = 0
    increment = 0.5   # must be 1 or 0.5
    isHalfStar = True

    # values you can change
    showCancel = True        # enable/disable the cancel link
    showAverageStars = True  # enable/disable the average stars
    
    # predefined css classes, see rating.css
    ratableStarCSS = 'ratable'
    averageStarCSS = 'average'
    starCSS = 'star'
    leftStarCSS = 'star-left'
    rightStarCSS = 'star-right'
    activeCSS = 'on'

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(RatingWidget, self).update()
        dm = zope.component.getMultiAdapter(
            (self.context, self.field), z3c.form.interfaces.IDataManager)
        self.converter = dm.query()
        self.average = self.converter.average
        self.current = self.converter.getRating(self.request.principal.id)
        self.maxScore = self.converter.scoreSystem.maxScore
        self.scores = self.converter.scores

    def extract(self):
        """See interfaces.IDataConverter"""
        # we do not support any value, we only set rating with JSON-RPC
        # return None which forces to call RatingDataConverter.toFieldValue
        return None

    @property
    def averageStars(self):
        if self.showAverageStars:
            result = u''
            for score in self.scores:
                if self.average < 0:
                    css = self.getStarCSS()
                        
                elif score.value <= self.average:
                    css = self.getStarCSS(self.activeCSS)
    
                elif score.value > self.average:
                    css = self.getStarCSS()
    
                result += self.getStarTag(score.key, css)
    
            return renderElement('div', cssClass=self.averageStarCSS,
                contents=result)

    @property
    def cancel(self):
        if self.showCancel:
            label = zope.i18n.translate(interfaces.CANCEL_RATING_LABEL,
                context=self.request)
            return u'<div class="cancel"><a href="#%s">%s</a></div>' % (
                interfaces.CANCEL_RATING_KEY, label)

    @property
    def ratableStars(self):
        result = u''
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return result

        for score in self.scores:

            if self.current < 0:
                css = self.getStarCSS()
                    
            elif score.value <= self.current:
                css = self.getStarCSS(self.activeCSS)

            elif score.value > self.current:
                css = self.getStarCSS()

            result += self.getStarTag(score.key, css, True)

        return renderElement('div', id=self.id, cssClass=self.ratableStarCSS,
            contents=result)

    def getStarCSS(self, activeCSS=''):
        """Knows how to switch left and right star css classes."""
        if self.isHalfStar and self._leftStarFlag:
            css = '%s %s %s' % (self.starCSS, self.leftStarCSS, activeCSS)
            self._leftStarFlag = False
        elif self.isHalfStar and not self._leftStarFlag:
            css = '%s %s %s' % (self.starCSS, self.rightStarCSS, activeCSS)
            self._leftStarFlag = True
        else:
            css = '%s %s' % (self.starCSS, activeCSS)
        return css.strip()

    def getStarLink(self, scoreKey):
        """Create a ratable star link tag."""
        url = u'#%s' % scoreKey
        label = zope.i18n.translate(_(u'Rate me'), context=self.request)
        return u'<a href="%s">%s</a>' % (url, label)

    def getStarTag(self, scoreKey, css, ratable=False):
        """Create a ratable star div tag."""
        if ratable:
            starContent = self.getStarLink(scoreKey)
        else:
            starContent = u'&nbsp;'
        return renderElement('div', cssClass=css, contents=starContent)

    @property
    def j01RaterId(self):
        return 'j01Rater-%s' % self.id

    @property
    def jsonRPCURL(self):
        return absoluteURL(self.form, self.request)

    @property
    def javaScript(self):
        lines = []
        append = lines.append
        append("\n    fieldName: '%s'" % self.__name__)
        append("\n    url: '%s'" % self.jsonRPCURL)
        append("\n    curvalue: %s" % self.current)
        append("\n    increment: %s" % self.increment)
        code = ','.join(lines)
        return j01_rater_template % (self.j01RaterId, code)


@zope.component.adapter(interfaces.IFiveStarRatingField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def FiveStarRatingFieldWidget(field, request):
    """IFieldWidget factory for IRatingWidget."""
    widget = RatingWidget(request)
    widget.increment = 1
    widget.isHalfStar = False
    return FieldWidget(field, widget)

getFiveStarRatingWidget = FiveStarRatingFieldWidget


@zope.component.adapter(interfaces.IFiveHalfStarRatingField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def FiveHalfStarRatingFieldWidget(field, request):
    """IFieldWidget factory for IRatingWidget."""
    widget = RatingWidget(request)
    widget.increment = 0.5
    widget.isHalfStar = True
    return FieldWidget(field, widget)

getFiveHalfStarRatingWidget = FiveHalfStarRatingFieldWidget


@zope.component.adapter(interfaces.IFiveHalfStarFullRatingField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def FiveHalfStarFullRatingFieldWidget(field, request):
    """IFieldWidget factory for IRatingWidget."""
    widget = RatingWidget(request)
    widget.increment = 1
    widget.isHalfStar = True
    return FieldWidget(field, widget)

getFiveHalfStarFullRatingWidget = FiveHalfStarFullRatingFieldWidget


class RatingDataConverter(object):
    """Data converter for RatingConverter readonly field."""

    zope.interface.implements(IDataConverter)
    zope.component.adapts(interfaces.IRatingField, IWidget)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return value

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        # we do not support any value, we only set rating with JSON-RPC
        # Return NOT_CHANGED which prevents to set any value in applyChanges
        return z3c.form.interfaces.NOT_CHANGED

    def __repr__(self):
        return '<%s converts from %s to %s>' %(
            self.__class__.__name__,
            self.field.__class__.__name__,
            self.widget.__class__.__name__)


# TODO: move this to p01.form as a generic lib
def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it."""
    attr_list = []

    # special case handling for cssClass
    cssClass = kw.pop('cssClass', u'')

    # If the 'type' attribute is given, append this plus 'Type' as a
    # css class. This allows us to do subselector stuff in css without
    # necessarily having a browser that supports css subselectors.
    # This is important if you want to style radio inputs differently than
    # text inputs.
    cssWidgetType = kw.get('type', u'')
    if cssWidgetType:
        cssWidgetType += u'Type'
    names = [c for c in (cssClass, cssWidgetType) if c]
    if names:
        attr_list.append(u'class="%s"' % u' '.join(names))

    style = kw.pop('style', u'')
    if style:
        attr_list.append(u'style=%s' % quoteattr(style))

    # special case handling for extra 'raw' code
    if 'extra' in kw:
        # could be empty string but we don't care
        extra = u" " + kw.pop('extra')
    else:
        extra = u''

    # handle other attributes
    if kw:
        items = kw.items()
        items.sort()
        for key, value in items:
            if value is None:
                warnings.warn(
                    "None was passed for attribute %r.  Passing None "
                    "as attribute values to renderTag is deprecated. "
                    "Passing None as an attribute value will be disallowed "
                    "starting in Zope 3.3."
                    % key,
                    DeprecationWarning, stacklevel=2)
                value = key
            attr_list.append(u'%s=%s' % (key, quoteattr(unicode(value))))

    if attr_list:
        attr_str = u" ".join(attr_list)
        return u"<%s %s%s" % (tag, attr_str, extra)
    else:
        return u"<%s%s" % (tag, extra)


def renderElement(tag, **kw):
    contents = kw.pop('contents', None)
    if contents is not None:
        # Do not quote contents, since it often contains generated HTML.
        return u"%s>%s</%s>" % (renderTag(tag, **kw), contents, tag)
    else:
        return renderTag(tag, **kw) + " />"
