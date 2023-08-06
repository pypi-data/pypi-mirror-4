# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import z3c.form.interfaces
import zope.schema.interfaces


class IAutocompleteWidget(z3c.form.interfaces.IWidget):
    """Autocomplete widget"""


class ISearchableSource(zope.schema.interfaces.IIterableSource):
    """A source suitable for autocompletion.
    Note that its __contains__() method should always return True.
    """

    def search(prefix):
        """Returns a list of values from this source that match the given
        prefix."""
