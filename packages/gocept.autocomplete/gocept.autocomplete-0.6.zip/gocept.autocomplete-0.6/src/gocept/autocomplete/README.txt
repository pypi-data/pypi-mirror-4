Autocomplete widget
===================

gocept.autocomplete provides an autocomplete widget for z3c.form.
The widget is useful if you want to provide the user with a list of suggestions
for a field, but still want to accept anything else that is entered, too.
The UI-part of the widget is YUI AutoComplete <http://developer.yahoo.com/yui/autocomplete/>.

``zc.resourcelibrary`` is used to integrate the YUI library in HTML, so this
package is incompatible with packages using ``hurry.resource``.

To use the widget, `<include package="gocept.autocomplete">` and provide a
source that implements `gocept.autocomplete.interfaces.ISearchableSource`.
This means two things, one, your source must provide a search() method so it can
be queried for values (with whatever has been entered so far as the query) and
two, you must always return True from the __contains__() method, so that the
user is free to enter a value that is not part of the suggestions.

No further configuration is required, the widget is automatically registered for
all `zope.schema.IChoice` fields with an `ISearchableSource`.

As an example, we exercise the code from `gocept.autocomplete.tests.color` with
the testbrowser:

>>> import zope.app.testing.functional
>>> root = zope.app.testing.functional.getRootFolder()
>>> import gocept.autocomplete.tests.color
>>> house = gocept.autocomplete.tests.color.House()
>>> root['house'] = house

>>> import zope.testbrowser.testing
>>> b = zope.testbrowser.testing.Browser()
>>> b.handleErrors = False

The AutocompleteWidget is an enhanced TextWidget. Thus, in display mode, it
behaves just like a TextWidget:

>>> b.open('http://localhost/house')
>>> print b.contents
<?xml...
...<span id="form-widgets-color" class="text-widget autocomplete required choice-field"></span>...

But in edit mode, it generates additional javascript code:

>>> b.addHeader('Authorization', 'Basic mgr:mgrpw')
>>> b.open('http://localhost/house')
>>> print b.contents
<?xml...
...<script src=".../autocomplete-min.js"...
...<input id="form-widgets-color"...
...<div id="form-widgets-color-container"...
...DS_XHR("http://localhost/house/@@index.html/++widget++color/@@autocomplete-search"...
...new YAHOO.widget.AutoComplete( "form-widgets-color", "form-widgets-color-container"...

The autocompletion is populated via a view registered on the widget:

>>> b.open('http://localhost/house/@@index.html/++widget++color/@@autocomplete-search')
>>> print b.contents
>>> b.open('http://localhost/house/@@index.html/++widget++color/@@autocomplete-search?q=r')
>>> print b.contents
red
ruby

But we can still enter any value we want and have it saved (there are two parts
to make this work, one is that the source must always return True in its
__contains__() method, and the other is that the widget uses a special
TitledTokenizedTerm that uses the actual value for everything):

>>> b.open('http://localhost/house')
>>> b.getControl('Color').value = 'foo'
>>> b.getControl(name='form.buttons.apply').click()
>>> print b.contents
<?xml...
...foo...


Grouped Forms
=============

A special case are group forms, who provide the field definitions in
their groups. For this particular occasion, we've setup an
ApartmentGroup and a form:

>>> apartment = gocept.autocomplete.tests.color.Apartment()
>>> root['apartment'] = apartment

The widget traversal for grouped forms returns the correct search
results:

>>> b.open('http://localhost/apartment/@@grouped.html/++widget++color/@@autocomplete-search?q=r')
>>> print b.contents
red
ruby
>>> b.open('http://localhost/apartment/@@grouped.html/++widget++number/@@autocomplete-search?q=1')
>>> print b.contents
12A
12
