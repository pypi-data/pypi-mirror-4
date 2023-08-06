# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.autocomplete.testing
import unittest


@unittest.skip('foo')
class AutocompleteTest(gocept.autocomplete.testing.SeleniumTestCase):

    def test_autocomplete(self):
        s = self.selenium

        # XXX: logging in this way on /demo directly (which does not *require*
        # login) does not work
        s.open('http://mgr:mgrpw@%s/manage' % self.selenium.server)

        s.open('/demo')
        # XXX: this *looks* like we're entering 'rr' (when one observes the
        # browser), but it does the right thing -- and all other combination
        # of calls I tried didn't work at all. :-(
        s.type('id=form-widgets-color', 'r')
        s.typeKeys('id=form-widgets-color', 'r')
        s.waitForValue('id=form-widgets-color', 'red')
        s.verifyText('id=form-widgets-color-container', '*red*')
