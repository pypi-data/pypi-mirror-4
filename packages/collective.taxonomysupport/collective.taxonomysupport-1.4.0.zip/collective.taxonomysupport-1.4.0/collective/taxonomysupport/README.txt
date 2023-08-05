Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.open(portal_url+'/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

    >>> "You are now logged in" in browser.contents
    True
    >>> browser.open(portal_url)

Here, we set the value of the fields on the login form and then simulate a
submit click.


Test if taxonomy support works with default pages and so on

    >>> from collective.taxonomysupport.interfaces import ITaxonomyLevel

    >>> self.setRoles(('Contributor', 'Manager' ))
    >>> self.portal.invokeFactory(type_name='Folder', id='myfolder')
    'myfolder'
    >>> myfolder = getattr(self.portal, 'myfolder')
    >>> myfolder.invokeFactory(type_name='Document', id='mydoc', title='My Doc')
    'mydoc'
    >>> mydoc = getattr(myfolder, 'mydoc')
    >>> myfolder.setDefaultPage('mydoc')

    >>> browser.open(myfolder.absolute_url())

    >>> "My doc" in browser.contents
    False

    >>> myfolder.getDefaultPage()
    'mydoc'

    >>> ITaxonomyLevel.providedBy(myfolder)
    False

    >>> browser.getLink('Add to taxonomy roots').click()
    >>> ITaxonomyLevel.providedBy(myfolder)
    True

    >>> myfolder.restrictedTraverse('@@mark_taxonomy_root')()

As we can see, if we have a front page for the folder he don't get the Taxonomy
interfaces

    >>> ITaxonomyLevel.providedBy(mydoc)
    False

    >>> browser.getLink('Remove from taxonomy roots').click()
    >>> ITaxonomyLevel.providedBy(myfolder)
    False
    
    >>> ITaxonomyLevel.providedBy(mydoc)
    False



-*- extra stuff goes here -*-

