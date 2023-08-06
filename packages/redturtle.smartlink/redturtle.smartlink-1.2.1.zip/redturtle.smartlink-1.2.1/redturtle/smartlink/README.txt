.. contents:: **Table of contents**

=====================================
How to use Smart Link - documentation
=====================================

Before beginning our tour, let's configure some of the underlying stuff.

    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> self.portal.error_log._ignored_exceptions = ()
    >>> browser.open(portal_url)

Let's log in. 

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

We ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

Let's go to the portal root.

    >>> browser.getLink('Home').click()

Basic use of Smart Link
=======================

First of all, explore the Smart Link features as new Plone content type.

Use Smart Link as ATLink replacement
------------------------------------

We use the "*Add new*" menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
**Link** and click the *Add* button to get to the add form.

    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()

We select **Link** because Smart Link replace the basic ATLink completly, stealing it's name and
underlying type infos. This is quite good, as every 3rd-party products that can behave integration
with basic ATLink content, will also works well with Smart Link.

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Remote link: sample 1'

We can't only provide the content title; even if the Plone UI display only the "*Title*" as required
field, you can save the link only providing at least a remote or internal link.

    >>> browser.getControl('Save').click()
    >>> 'Please provide the external URL, or fill the "Internal link" field' in browser.contents
    True
    >>> 'Please provide the internal link, or fill the "External link" field' in browser.contents
    True

In the same time, we can't provide both internal or external data. Smart Link will be confused, not able
to understand what to use.

    >>> browser.getControl('External link').value = portal_url + '/contact-info'
    >>> news = portal.unrestrictedTraverse('news')
    >>> browser.getControl(name='internalLink').value = news.UID()
    >>> browser.getControl('Save').click()
    >>> 'You must select an internal link or enter an external link. You cannot have both.' in browser.contents
    True

In this first example we provide the *External link* information (so we need to empty the *Internal link*):

    >>> browser.getControl('External link').value = portal_url + '/contact-info'
    >>> browser.getControl(name='internalLink').value = ''
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Another important ATLink (and so Smart Link) feature is the auto-redirection in some cases. Now we are
site manager and also we can modify the link, so we are only warned.

    >>> "You see this page because you have permission to edit this link." in browser.contents
    True
    >>> browser.url == portal_url + '/remote-link-sample-1'
    True

We aren't redirected to the link target now, and we will not also if we click again on the link.

    >>> browser.getLink('Remote link: sample 1').click()
    >>> browser.url == portal_url + '/remote-link-sample-1'
    True

To test this feature we need a different user, and visit the link with this user.
Let's publish the link, then change user.

    >>> browser.getLink('Publish').click()
    >>> 'Item state changed.' in browser.contents
    True
    >>> browser.getLink('Log out').click()
    >>> 'You are now logged out' in browser.contents
    True
    >>> browser.open(portal_url)
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = 'contributor'
    >>> browser.getControl('Password').value = default_password
    >>> browser.getControl('Log in').click()
    >>> 'You are now logged in' in browser.contents
    True

Let's now move to the link:

    >>> browser.getLink('Remote link: sample 1').click()
    >>> browser.url == portal_url + '/contact-info'
    True

As you see now we are in the target page, not in the link context.

We can now continue all other tests with our Manager user.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = portal_owner
    >>> browser.getControl('Password').value = default_password
    >>> browser.getControl('Log in').click()
    >>> 'You are now logged in' in browser.contents
    True

Additional image fields
-----------------------

Smart link give to the contributor some additional fields, better described in the `product documentation`__.

__ http://pypi.python.org/pypi/redturtle.smartlink
    
Here we simply test the usage of those new fields.

First of all, Smart Link give a new **image** and **image caption** field as *Plone "News Item"* does.

Let's add a new image and caption to our link.

    >>> browser.getLink('Remote link: sample 1').click()
    >>> browser.getLink('Edit').click()
    >>> import cStringIO
    >>> imagefile = cStringIO.StringIO(self.getImage())
    >>> image_control = browser.getControl(name='image_file')
    >>> image_control.add_file(imagefile, 'image/png', 'plone_logo.png')
    >>> browser.getControl('Image Caption').value = "A not-so-remote link to our contact info form"
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True
    
We need also to test if our link really behave an image now:
    
    >>> contactinfo_link = portal['remote-link-sample-1']
    >>> contactinfo_link.unrestrictedTraverse('image_large')
    <Image... at /plone/remote-link-sample-1/image_large>

Now the Smart Link view also display the image and the caption under it in the item's view:

    >>> browser.url == portal_url + '/remote-link-sample-1'
    True
    >>> print browser.contents.strip() # please, don't laugh
    <!DOCTYPE html...
    ...
    <img src=".../remote-link-sample-1/image_mini" alt="Remote link: sample 1" title="A not-so-remote link to our contact info form" ... />...
    ...
    ...</html>

The link icon
-------------

Another minor feature is related to the customization of the link icon. Normally a Plone ATLink will show a
standard type image for all links, and the same is for Smart Link contents.

But with Smart Link, if you want to show another customized icon, you can. The icon image chosen as icon
will override the one from the Plone *getIcon* method, so it will be used in Plone views.

Use this, for example, to show the *favicon* of the remote site. Let's personalize the icon of our link:

    >>> browser.getLink('Edit').click()
    >>> imagefile = cStringIO.StringIO(self.getImage())
    >>> image_control = browser.getControl(name='favicon_file')
    >>> image_control.add_file(imagefile, 'image/png', 'plone_logo.png')
    >>> browser.getControl('Save').click()
    >>> favicon = contactinfo_link.unrestrictedTraverse('favicon')
    >>> favicon
    <Image at .../remote-link-sample-1/favicon>

As the image here is used for replace an icon (where in Plone is 16x16px sized), the uploaded image will be
replaced and saved with a 16x16 ones. Smart Link will not allow you to put there bigger images.

    >>> favicon.width
    16
    >>> favicon.height
    16

To see that the favicon chosen is also used as Plone content icon, let's go on a view that use this
information:

    >>> browser.open(portal_url + '/folder_listing')
    >>> print browser.contents.strip()
    <!DOCTYPE html...
    ...
    <img ... width="16" height="16" src=".../remote-link-sample-1/favicon" ... />
    ...
    ...</html>

Smart Link main feature: internal link
======================================

The new features above are only minor features that cover some specific needs. The main feature of Smart
Link (that lead to it's name, so a Plone Link that is "smart and cool", because it maintain the linked URL)
is when it's used for *internal link to a Plone site content*.

You can use your Link content type and reference (without manually write down its URL) another content
of the site.

First of all we need a new content, and we will put it inside a Folder:

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Folder').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'Foo folder'
    >>> browser.getControl('Save').click()
    >>> browser.url == portal_url + '/foo-folder/'
    True
    >>> browser.getLink('Publish').click()
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Page').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'My manual'
    >>> browser.getControl('Body Text').value = """<h2>Welcome!</h2>
    ... <h3><a name="section-1"></a>Section 1</h3>
    ... <p>Lorem ipsum...</p>"""
    >>> browser.getControl('Save').click()
    >>> browser.url == portal_url + '/foo-folder/my-manual'
    True
    >>> browser.getLink('Publish').click()

Use the internal link
---------------------

Now we can create a new internal link to our page:

    >>> browser.open(portal_url)
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl(name='title').value = 'Internal link: sample 2'

In a Javascript-enabled browser you can use the **Internal link** field to navigate the site and find
what you want to link.

    >>> mmanual = portal.unrestrictedTraverse("foo-folder/my-manual")
    >>> browser.getControl(name='internalLink').value = mmanual.UID()
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True
    >>> mmanual.absolute_url() in browser.contents
    True
    >>> browser.getLink('Publish').click()

Keep the internal link reference
--------------------------------

In early releases, Smart Link wanted only to help users to create internal links without manually copy/paste
URLs, so if the referenced document was deleted or moved after the linking action, you were not helped
in keeping this reference.

Recently a more permanent relation is kept between the two contents. To prove this let's first create
another Smart Link that refer to the same document, but in a different way:

    >>> browser.open(portal_url)
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl(name='title').value = 'Almost internal link: sample 3'
    >>> browser.getControl('External link').value = portal_url + '/foo-folder/my-manual'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True
    >>> mmanual.absolute_url() in browser.contents
    True
    >>> browser.getLink('Publish').click()

We created an internal link in the basic Plone way: creating an external link to a site content's URL.
Apart the boring procedure you must follow doing this (you need to remember and copy/paste the content's
URL), we can have broken link problem.

To prove that, from the visitor point of view, this don't change anything, we can log-off then test links
as anonymous user.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getLink('Internal link: sample 2').click()
    >>> browser.url == portal_url + '/foo-folder/my-manual'
    True
    >>> browser.getLink('Almost internal link: sample 3').click()
    >>> browser.url == portal_url + '/foo-folder/my-manual'
    True

Ok, but what really change also is a mechanism that keep a sort of link integrity. Let's log-in again
as site administrator.

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

First of all, when a site content is "*smart linked*" from a Smart Link, it's marked with a special
interface.

    >>> from redturtle.smartlink.interfaces import ISmartLinked
    >>> ISmartLinked.providedBy(mmanual)
    True

This marker make some of the magic. A set of events are related to actions taken on contents that
behave those markers.

For example what's happen when you move (or rename, it's the same...) the referenced content?

    >>> browser.open(portal_url + '/foo-folder/my-manual')
    >>> browser.getLink('Rename').click()
    >>> browser.getControl('New Short Name').value = 'my-foo-manual'
    >>> browser.getControl('Rename All').click()
    >>> "Renamed 'my-manual' to 'my-foo-manual'." in browser.contents
    True

See that Smart Link keep the relation alive:

    >>> browser.getLink('Internal link: sample 2').click()
    >>> slink = portal['internal-link-sample-2']
    >>> slink.getRemoteUrl() == portal_url + '/foo-folder/my-foo-manual'
    True
    >>> slink.getField('remoteUrl').get(slink) == portal_url + '/foo-folder/my-foo-manual'
    True

But before test this as anonymous, let me do something I will explain later.
I create a new fake content with the same id of the one we renamed:

    >>> browser.open(portal_url + '/foo-folder')
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Page').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'My manual'
    >>> browser.getControl('Body Text').value = "<p>I'm not the REAL manual, just a fake!</p>"
    >>> browser.getControl('Save').click()
    >>> browser.getLink('Publish').click()

Ok. Now: to show what can be bad with basic Plone ATLink used for internal link, we log-off again and we
use our Smart Link.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getLink('Internal link: sample 2').click()
    >>> browser.url == portal_url + '/foo-folder/my-foo-manual'
    True

Wow, the first test is ok. The internal link was aware of the URL change of the linked page!
And the "normal" link?

    >>> browser.getLink('Almost internal link: sample 3').click()
    >>> browser.url == portal_url + '/foo-folder/my-foo-manual'
    False
    >>> browser.url == portal_url + '/foo-folder/my-manual'
    True
    >>> "I'm not the REAL manual, just a fake!" in browser.contents
    True

As expected, it didn't work. We are now on the new content, the fake document.

But why we created it?

In facts, the normal links approach *can* works normally even for internal link and if the target object
is moved, because Plone has an internal mechanism that automatically make aliases for content that changed
their URLs (the `plone.app.redirector`__ package manage this feature).

__ http://pypi.python.org/pypi/plone.app.redirector

This is a good solution that Plone give us, but it's not perfect:

* you will have problems if you loose the data inside the Redirection utility
* more probable, you will have problem if another content will use the same URL in future

For a good reason, if your old URL will be taken by a new content, you will reach the new content using it.
Obviously the *real* object with the same URL wins on *fake* object that held this URL some time ago...

The relation from the linked content back to the Smart Link
-----------------------------------------------------------

Some action are taken also when you touch Smart Link. If you delete a Smart Link that held an internal
link to a site's content, the referenced object is "cleaned", and the marker interface removed.

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.getLink('Internal link: sample 2').click()
    >>> browser.getLink('Delete').click()
    >>> browser.getControl('Delete').click()
    >>> 'Internal link: sample 2 has been deleted.' in browser.contents
    True
    >>> ISmartLinked.providedBy(mmanual)
    False

In the same way, if I create a Smart Link for an internal reference, then I change it to link another
content or to a remote URL, all interfaces must always be removed.

So, we create a new Smart Link to see this in action.

    >>> browser.open(portal_url + '/foo-folder')
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'Yet another internal link: sample 4'
    >>> ffolder = portal.unrestrictedTraverse("foo-folder")
    >>> browser.getControl(name='internalLink').value = ffolder.UID()
    >>> browser.getControl('Save').click()
    >>> ffolder.absolute_url() in browser.contents
    True
    >>> browser.getLink('Publish').click()
    >>> ISmartLinked.providedBy(ffolder)
    True

The first test: we simply smart link something else.

    >>> browser.getLink('Edit').click()
    >>> index = portal.unrestrictedTraverse("front-page")
    >>> browser.getControl(name='internalLink').value = index.UID()
    >>> browser.getControl('Save').click()
    >>> index.absolute_url() in browser.contents
    True
    >>> ISmartLinked.providedBy(ffolder)
    False
    >>> ISmartLinked.providedBy(index)
    True

We see that the unlink procedure also remove the marker.

We can also change the internal link to an external, remote URL. Let's try this.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='internalLink').value = ''
    >>> browser.getControl('External link').value = 'http://planet.plone.org/'
    >>> browser.getControl('Save').click()
    >>> 'http://planet.plone.org/' in browser.contents
    True
    >>> ISmartLinked.providedBy(index)
    False

Administrative features: handle back-end/front-end URLs
=======================================================

The use of Link in Plone became problematic when your site handle different host domain. Commonly you know
how your public site/intranet will be used from users. So: you know you have one common hostname
(like: http://intranet.mycompany.com/). With Plone and ATLink you will have problem if you add to the site
new link using a non-official/non-final hostname (e.g: you begin adding contents when you still developing
in "localhost").

Also: many structured companies can manage a web site using different URLs from the front-end (the URL
that site's visitors use) and back-end (also know as back-office, the URL used only internally, for
managing the site itself).

Again, basic Plone ATLink are not good in those cases. The site contributor not only need to manually copy
the link resource, but also need to change it from the back-end version to the one that will be seen in
the front-end.

As said above Smart Link is only something more that a Plone ATLink so it suffer the same plague. But even
if the Link content type itself will not help you in this, we provided a configuration tool that will help
you preventing those possible errors.

Using and configuring the "*Configure Smart Link*" section will make you site's contributors happy again.

    >>> browser.getLink('Site Setup').click()
    >>> browser.getLink('Configure Smart Link').click()    
    >>> 'Smart Link configuration' in browser.contents
    True

Simple case: you know your official site URL
--------------------------------------------

As said above, let's now suppose to be in an intranet that will be publishes as *http://intranet.mycompany.com/*.
We know that every internal link *must* begin with this URL.

Let now suppose that a user works onto this intranet from a staging URL as *localhost*.

    >>> browser.getControl('Front-end main URL').value = 'http://intranet.mycompany.com'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True

Now let's bo back to site root for making an internal link.

    >>> browser.open(portal_url)
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'Transformed official internal link: sample 5'
    >>> browser.getControl(name='internalLink').value = ffolder.UID()
    >>> browser.getControl('Save').click()
    >>> '<a href="http://intranet.mycompany.com/foo-folder"...>Foo folder</a>' in browser.contents
    False

As the link is now internal, we don't have a raw URL but a pretty link on the title

    >>> 'This is an internal link to &quot;<a href="http://intranet.mycompany.com/foo-folder" title="">Foo folder</a>&quot;' in browser.contents
    True

So: without a not-so-complex configuration we have now a set-up that will automatically handle internal links.

Advanced case: back-end/fron-end transformation
-----------------------------------------------

Now we see the more advanced case.

    >>> browser.getLink('Site Setup').click()
    >>> browser.getLink('Configure Smart Link').click()    
    >>> 'Smart Link configuration' in browser.contents
    True
    >>> browser.getControl('Front-end main URL').value = ''

Now we need to provide a list of back-end URLs. They must be all the URLs we know that are used
in back-end. Let's say that our first back-end URL will be "*http://backend*" and the hostname we used
right now.

Can we also add two or more times the same URL?

    >>> browser.getControl('Add Back-end URLs').click()
    >>> browser.getControl(name='form.backendlink.0.').value = 'http://backend'
    >>> browser.getControl('Add Back-end URLs').click()
    >>> browser.getControl(name='form.backendlink.1.').value = 'http://backend'
    >>> browser.getControl('Save').click()    
    >>> 'One or more entries of sequence are not unique.' in browser.contents
    True

Well... no. A back-end link will be unique and transformed only in a front-end ones. However front-end
links can be duplicated.

    >>> browser.getControl(name='form.backendlink.1.').value = portal.REQUEST['URL']
    >>> browser.getControl('Save').click()
    >>> 'There were errors' in browser.contents
    True

We still have error because for every back-end link we must provide a front-end transformation (even if
duplicated)

    >>> browser.getControl('Add Front-end URLs').click()
    >>> browser.getControl(name='form.frontendlink.0.').value = 'http://127.0.0.1'
    >>> browser.getControl('Save').click()
    >>> 'There were errors' in browser.contents
    True
    >>> browser.getControl('Add Front-end URLs').click()
    >>> browser.getControl(name='form.frontendlink.1.').value = 'http://127.0.0.1'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True

Ok. Those changes are valid only from now to the future, but if you wanna update all already present
Smart Link, you can use the configuration panel itself: the "*Update existing links*" button.

    **Be aware** that this will index again all Smart Link in the site. This is not dangerous, but
    remember to perform this from a back-end URL.
    If you run this (for example) from "http://localhost..." because you are accessing the site using
    an SSH tunnel, and the URL you are using is not in the back-end list, all your internal Smart Link
    will use "localhost"!

    >>> browser.getControl('Update existing links').click()

Now let's see what is changed in our links all around the site, going back to our third example.

    >>> browser.getLink('Almost internal link: sample 3').click()
    >>> print browser.contents.strip()
    <!DOCTYPE html...
    ...
    <a href="http://127.0.0.1/plone/foo-folder/my-manual" rel="external">http://127.0.0.1/plone/foo-folder/my-manual</a> 
    ...
    ...</html>

As you can see there also our fake internal link is changed. The configuration tool changed *all*
Smart Link where the transformation can be applied, without looking at the internal/external status.

This is good, because also users that don't know how to handle internal link are helped.

Obviously we don't need to run the migration tool when adding new links.

    >>> browser.open(portal_url)
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Link').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl('Title').value = 'Transformed internal link: sample 6'
    >>> browser.getControl(name='internalLink').value = ffolder.UID()
    >>> browser.getControl('Save').click()
    >>> 'This is an internal link to &quot;<a href="http://127.0.0.1/plone/foo-folder" title="">Foo folder</a>&quot;' in browser.contents    
    True

As said above, all new added links will feel the configuration settings.

The site-root based approach
----------------------------

The Smart Link configuration have another control we skipped above. Here we explain how it work and when
you can use it safely.

We are talking of the "*Relative links*" check.

When using this you can go over the back-end/front-end problem above.

    >>> browser.getLink('Site Setup').click()
    >>> browser.getLink('Configure Smart Link').click()
    >>> browser.getControl('Relative links').click()
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True

As the last configuration option, this change will be applied to all future links, or also to current
ones if we use the "*Update existing links*" command again. This option however make differences only
to internal link.

    >>> browser.getControl('Update existing links').click()
    >>> browser.getLink('Transformed internal link: sample 6').click()
    >>> 'This is an internal link to &quot;<a href="/plone/foo-folder" title="">Foo folder</a>&quot;' in browser.contents    
    True

So all internal link are now relative link based on the Plone portal root.

We see also that this option override all other options we have added to the "*Back-end Link*" and
"*Front-end Link*" sections.

This configuration has a *drawback*. Whatever is you portal URL, if you use a *virtual_hosting* or not,
links will be always like this, with the "/*portalid*" in front of it.

You can fix this problem (no one want to see URL like "http://myhost.com/uselessid/foo"), but you are
forced to configure your Apache to perform some URL rewrite.

Also this option break a little the Smart Link idea: keep the new Link content type a simple URL
container like the ATLink is.

However: this kind of configuration is never unconsistent; you will never find situations where the
URL saved in the catalog is not what you expects. Instead this can happens if you badly configure options
above (or forget to configure at all).

----

That's all!

