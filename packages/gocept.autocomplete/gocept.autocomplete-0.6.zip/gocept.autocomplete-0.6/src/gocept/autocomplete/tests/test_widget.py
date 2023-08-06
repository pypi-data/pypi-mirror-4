# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.traversing.api import traverse
import gocept.autocomplete.testing
import gocept.autocomplete.tests.color
import gocept.autocomplete.widget
import unittest
import z3c.form.interfaces
import z3c.form.testing
import zope.app.testing.functional
import zope.interface
import zope.publisher.browser
import zope.schema
import zope.traversing.adapters
import zope.traversing.interfaces


class WidgetTest(zope.app.testing.functional.FunctionalTestCase):
    layer = gocept.autocomplete.testing.functional_layer

    def setUp(self):
        super(WidgetTest, self).setUp()
        z3c.form.testing.setupFormDefaults()

    def test_sources_value_are_not_converted(self):
        request = z3c.form.testing.TestRequest()
        house = gocept.autocomplete.tests.color.House()
        house.color = u"red"
        form = gocept.autocomplete.tests.color.HouseForm(house, request)
        form.update()
        self.assertEqual(u"red", form.widgets['color'].value)

        request.form[form.widgets['color'].name] = u"foo"
        form.handleApply(form, None)
        self.assertEqual(u"foo", house.color)

    def test_traversal(self):
        request = z3c.form.testing.TestRequest()
        house = gocept.autocomplete.tests.color.House()
        zope.component.provideAdapter(
            zope.traversing.adapters.RootPhysicallyLocatable,
            (gocept.autocomplete.tests.color.House,),
            zope.traversing.interfaces.IPhysicallyLocatable)
        house.color = u"red"
        form = gocept.autocomplete.tests.color.HouseForm(house, request)
        zope.component.provideAdapter(
            lambda x,y: form,
            (gocept.autocomplete.tests.color.House, z3c.form.testing.TestRequest),
            zope.interface.Interface,
            name='form'
            )
        # we intentionally don't call form.update() ourselves,
        # since the traverser shouldn't assume that it has been called
        actual = traverse(house, '/@@form/++widget++color', request=request)
        self.assertEqual(form.widgets['color'], actual)
