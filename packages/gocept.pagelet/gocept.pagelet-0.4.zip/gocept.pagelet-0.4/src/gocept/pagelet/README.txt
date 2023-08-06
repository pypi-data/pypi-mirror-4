=============================
Easy z3c.pagelet registration
=============================

The `<gocept:pagelet>` directive allows easier registration of
z3c.pagelets. It behaves quite like `<browser:page>`.

Setup
=====

We need some zcml setup:

>>> import sys
>>> from zope.configuration import xmlconfig
>>> import gocept.pagelet
>>> context = xmlconfig.file('meta.zcml', gocept.pagelet)


Template only
=============

It is possible to just use a template as pagelet. A class is not required:

>>> context = xmlconfig.string("""
... <configure
...     xmlns:gocept="http://namespaces.gocept.com/zcml">
...   <gocept:pagelet
...       name="index.html"
...       for="*"
...       permission="zope.Public"
...       template="test-template.pt"
...       />
... </configure>
... """, context)

We should now have a page:

>>> import zope.component
>>> from zope.publisher.browser import TestRequest
>>> pagelet = zope.component.getMultiAdapter(
...     (object, TestRequest()), name='index.html')
>>> pagelet
<gocept.pagelet.zcml.SimplePagelet from .../gocept/pagelet/test-template.pt object at 0x...>
>>> pagelet.__name__
u'index.html'

When we render the pagelet the test-template is used:

>>> pagelet.render()
u'Hello from the test template.\n'


Class only
==========

Of course it's also possible to register a class without a template. Create a
class and make it available in a module:


>>> from z3c.pagelet.browser import BrowserPagelet
>>> class MyPagelet(BrowserPagelet):
...     """Custom pagelet"""
...     def render(self):
...         return u"Hello from the custom pagelet."""

Make it available under the fake package ``custom``:

>>> sys.modules['custom'] = type(
...     'Module', (),
...     {'MyPagelet': MyPagelet})()


Make it available via ZCML:

>>> context = xmlconfig.string("""
... <configure
...     xmlns:gocept="http://namespaces.gocept.com/zcml">
...   <gocept:pagelet
...       name="class.html"
...       for="*"
...       permission="zope.Public"
...       class="custom.MyPagelet"
...       />
... </configure>
... """, context)

Get the pagelet:

>>> pagelet = zope.component.getMultiAdapter(
...     (object, TestRequest()), name='class.html')
>>> pagelet
<gocept.pagelet.zcml.MyPagelet object at 0x...>
>>> pagelet.render()
u'Hello from the custom pagelet.'



Class and template
==================

It's for course also possible to specify both class and template. So create
another pagelet class and register it:

>>> class MyPagelet2(BrowserPagelet):
...     """Custom pagelet"""
...     i_am_very_custom = True
>>> sys.modules['custom'] = type(
...     'Module', (),
...     {'MyPagelet': MyPagelet2})()


Make it available via zcml:

>>> context = xmlconfig.string("""
... <configure
...     xmlns:gocept="http://namespaces.gocept.com/zcml">
...   <gocept:pagelet
...       name="class-template.html"
...       for="*"
...       permission="zope.Public"
...       class="custom.MyPagelet"
...       template="test-template.pt"
...       />
... </configure>
... """, context)

>>> pagelet = zope.component.getMultiAdapter(
...     (object, TestRequest()), name='class-template.html')
>>> pagelet
<gocept.pagelet.zcml.MyPagelet2 object at 0x...>
>>> pagelet.render()
u'Hello from the test template.\n'
>>> pagelet.i_am_very_custom
True
