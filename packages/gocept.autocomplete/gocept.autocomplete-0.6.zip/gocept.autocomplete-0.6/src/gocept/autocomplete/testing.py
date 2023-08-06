# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.autocomplete.tests
import gocept.selenium.ztk
import os
import z3c.form.form
import z3c.form.tests
import zope.app.testing.functional
import zope.component


class FunctionalLayer(zope.app.testing.functional.ZCMLLayer):
    def setUp(self):
        zope.app.testing.functional.ZCMLLayer.setUp(self)
        zope.component.provideAdapter(z3c.form.form.FormTemplateFactory(
            os.path.join(os.path.dirname(gocept.autocomplete.tests.__file__),
                         'layout.pt')))


ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
functional_layer = FunctionalLayer(
    ftesting_zcml, __name__, 'FunctionalLayer',
    allow_teardown=True)
selenium_layer = gocept.selenium.ztk.Layer(functional_layer)


class SeleniumTestCase(gocept.selenium.ztk.TestCase):

    layer = selenium_layer
