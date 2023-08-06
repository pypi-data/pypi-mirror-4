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

Because add-on themes or products may remove or hide the login portlet, this test will use the login form that comes with plone.  

    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.  We then ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

Finally, let's return to the front page of our site before continuing

    >>> browser.open(portal_url)

-*- extra stuff goes here -*-
The Blog Entry content type
===============================

In this section we are tesing the Blog Entry content type by performing
basic operations like adding, updadating and deleting Blog Entry content
items.

Adding a new Blog Entry content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Blog Entry' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Blog Entry').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Blog Entry' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Blog Entry Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Blog Entry' content item to the portal.

Updating an existing Blog Entry content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Blog Entry Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Blog Entry Sample' in browser.contents
    True

Removing a/an Blog Entry content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Blog Entry
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Blog Entry Sample' in browser.contents
    True

Now we are going to delete the 'New Blog Entry Sample' object. First we
go to the contents tab and select the 'New Blog Entry Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Blog Entry Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Blog Entry
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Blog Entry Sample' in browser.contents
    False

Adding a new Blog Entry content item as contributor
------------------------------------------------

Not only site managers are allowed to add Blog Entry content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Blog Entry' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Blog Entry').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Blog Entry' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Blog Entry Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Blog Entry content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Blog content type
===============================

In this section we are tesing the Blog content type by performing
basic operations like adding, updadating and deleting Blog content
items.

Adding a new Blog content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Blog' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Blog').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Blog' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Blog Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Blog' content item to the portal.

Updating an existing Blog content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Blog Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Blog Sample' in browser.contents
    True

Removing a/an Blog content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Blog
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Blog Sample' in browser.contents
    True

Now we are going to delete the 'New Blog Sample' object. First we
go to the contents tab and select the 'New Blog Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Blog Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Blog
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Blog Sample' in browser.contents
    False

Adding a new Blog content item as contributor
------------------------------------------------

Not only site managers are allowed to add Blog content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Blog' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Blog').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Blog' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Blog Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Blog content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



