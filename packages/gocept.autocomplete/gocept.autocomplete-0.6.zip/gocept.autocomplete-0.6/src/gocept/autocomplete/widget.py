# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.autocomplete.interfaces
import js.jqueryui
import json
import string
import z3c.form.browser.text
import z3c.form.converter
import z3c.form.interfaces
import z3c.form.widget
import zc.resourcelibrary
import zope.interface
import zope.pagetemplate.interfaces
import zope.publisher.browser
import zope.security.proxy


class AutocompleteWidget(z3c.form.browser.text.TextWidget):
    zope.interface.implements(
        gocept.autocomplete.interfaces.IAutocompleteWidget)

    _javascript = """
(function($) {

$('#' + '%(id)s').autocomplete({
    source: '%(url)s',
    minLength: %(minLength)s
});

}(jQuery));
"""

    def __init__(self, *args, **kw):
        super(AutocompleteWidget, self).__init__(*args, **kw)
        self.minQueryLength = 1
        self.addClass(u'autocomplete')

    def render(self):
        js.jqueryui.ui_autocomplete.need()
        js.jqueryui.ui_lightness.need()
        return super(AutocompleteWidget, self).render()

    def input_field(self):
        class Dummy(object):
            pass
        parent = Dummy()
        zope.interface.alsoProvides(parent, z3c.form.interfaces.ITextWidget)
        super_template = zope.component.getMultiAdapter(
            (self.context, self.request, self.form, self.field,
             parent),
            zope.pagetemplate.interfaces.IPageTemplate, name=self.mode)
        return super_template(self)

    def javascript(self):
        context_url = str(zope.component.getMultiAdapter(
            (self.form.context, self.request), name='absolute_url'))

        search_url = "%s/@@%s/++widget++%s/@@autocomplete-search" % (
            context_url, self.form.__name__, self.name.split('.')[-1])

        return self._javascript % dict(
            id=self.id, minLength=self.minQueryLength, url=search_url)


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        gocept.autocomplete.interfaces.ISearchableSource,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def AutocompleteFieldWidget(field, source, request):
    return z3c.form.widget.FieldWidget(field, AutocompleteWidget(request))


class SearchView(zope.publisher.browser.BrowserView):
    def __call__(self):
        # XXX security!!
        context = zope.security.proxy.removeSecurityProxy(self.context)
        query = self.request.get("term")
        if query:
            return json.dumps(context.field.source.search(query))
        else:
            return json.dumps([])
