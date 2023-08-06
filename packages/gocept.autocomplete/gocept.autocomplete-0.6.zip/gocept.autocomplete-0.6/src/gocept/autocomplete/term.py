# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""
Since we want to accept any value that the user entered, even if it is not
part of the source yet, we do not use terms/tokens as usual but rather use
the value itself for everything.
"""

import gocept.autocomplete.widget
import z3c.form.converter
import zope.browser.interfaces
import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.schema.interfaces


class IdentityTerm(object):
    zope.interface.implements(zope.schema.interfaces.ITitledTokenizedTerm)

    def __init__(self, value):
        self.value = value
        self.token = value
        self.title = value


class IdentityTerms(object):
    zope.interface.implements(zope.browser.interfaces.ITerms)
    zope.component.adapts(gocept.autocomplete.interfaces.ISearchableSource,
                          zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        pass

    def getTerm(self, value):
        return IdentityTerm(value)

    def getValue(self, token):
        return token


class SourceDataConverter(z3c.form.converter.BaseDataConverter):
    zope.component.adapts(zope.schema.interfaces.IChoice,
                          gocept.autocomplete.interfaces.IAutocompleteWidget)

    def toWidgetValue(self, value):
        return zope.component.getMultiAdapter(
            (self.field.source, self.widget.request),
            zope.browser.interfaces.ITerms).getTerm(value).token

    def toFieldValue(self, value):
        return zope.component.getMultiAdapter(
            (self.field.source, self.widget.request),
            zope.browser.interfaces.ITerms).getValue(value)

