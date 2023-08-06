# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface
import zope.security.proxy
import zope.traversing.interfaces


class WidgetTraversable(object):
    """Traverser from a z3c.form to its widgets.

    /context/@@form/++widget++fieldname is the widget belonging to the form
    field 'fieldname'.
    """

    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        # XXX security!!
        self.context = zope.security.proxy.removeSecurityProxy(context)
        self.request = request

    def traverse(self, name, remaining):
        form = self.context
        form.update()
        if hasattr(form, 'groups') and form.groups:
            widget = self.find_widget(form, name)
        else:
            widget = form.widgets[name]
        return widget

    def find_widget(self, form, name):
        for group in form.groups:
            widget = group.widgets.get(name)
            if widget:
                return widget
