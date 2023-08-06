.. contents :: :local:


Introduction
============

Carousel is a tool for featuring a rotating set of banner images in any section
of your Plone site.  Features:

 * Different sets of banners can be used in different sections of the site.

 * Banners can link to another page in the site, or an external URL.

 * Carousel provides options to customize the appearance of the banner as well
   as the length and type of transition.

 * An optional pager provides navigation among the banners.

 * Transition effects are implemented using the jQuery javascript library which
   is included with Plone, so they are pretty lightweight.

 * Banners do not rotate while the mouse cursor is hovering over the Carousel.

 * Banner and pager templates can be registered to customize the appearance of
   the Carousel.

 * Carousel implements jQuery events, allowing for integration with custom
   javascripts.

 * Carousel images can be lazily loaded, to conserve the user and the server bandwidth
   if the full carousel cycle is not shown

 * Carousel images can be made to appear in random order

Compatibility
=============

Carousel requires Plone 3.0 or greater, mainly because it renders itself in a
viewlet.


Installation
============

Add Products.Carousel to your buildout's list of eggs, and re-run buildout. If
you get version conflicts while running buildout, you can use a known good
version set to find versions compatible with plone.app.z3cform::

    http://good-py.appspot.com/release/plone.app.z3cform/0.5.0-1?plone=4.0.2

Start Zope, go to Site Setup -> Add-on Products in your Plone site and
install the Carousel product.


Using Carousel
==============

A `detailed guide to using Carousel <http://plone.org/products/carousel/documentation>`_
is available.


Detailed overview and tests
===========================

Configuring a Carousel banner folder
------------------------------------

The items displayed by Carousel are known as "Carousel Banners" and can exist
within a "Carousel Folder" in any section of the site.  For purposes of
demonstration, let's add a Carousel folder to the root of the site.

Carousel folders are a matter of configuration more than content, so they don't
appear on the Add menu. Instead, there is a 'Carousel' tab.  Clicking
it within a section that doesn't yet have a Carousel folder will result
in the creation of a new one::

  >>> browser.open('http://nohost/plone')
  >>> browser.getLink('Carousel').click()
  >>> browser.url
  'http://nohost/plone/carousel/@@edit-carousel'

The new folder should now provide the ICarouselFolder interface::

  >>> from Products.Carousel.interfaces import ICarouselFolder
  >>> ICarouselFolder.providedBy(self.portal.carousel)
  True

If, on the other hand, we're in a folder that already has a Carousel folder,
the existing one will be used::

  >>> browser.goBack()
  >>> browser.getLink('Carousel').click()
  >>> browser.url
  'http://nohost/plone/carousel/@@edit-carousel'

And if we try to configure Carousel while we're already doing so, nothing
should change::

  >>> browser.getLink('Carousel').click()
  >>> browser.url
  'http://nohost/plone/carousel/@@edit-carousel'

Adding a Carousel banner
------------------------

Now that we're within the Carousel folder, we can add a Carousel banner using
the add menu::

  >>> browser.getLink('Carousel Banner').click()
  >>> browser.url
  'http://nohost/plone/carousel/portal_factory/Carousel...Banner/carousel_banner.../edit'

We can set various things including a title, target URL, and image::

  >>> browser.getControl('Title').value = 'Pirates and Cowboys agree: Ninjas suck'
  >>> browser.getControl('Link URL').value = 'http://www.plone.org'
  >>> browser.getControl(name='image_file')
  <Control name='image_file' type='file'>
  >>> browser.getControl('Save').click()
  >>> 'Changes saved.' in browser.contents
  True

We need to publish the new banner.
  >>> browser.getLink('Publish').click()

Viewing the banners
-------------------

Now if we return to the home page, where we initially configured the banners,
the banner we just added should be rendered (*before* the tabs)::

  >>> browser.open('http://nohost/plone')
  >>> browser.contents
  <BLANKLINE>
  ...Pirates and Cowboys...
  ...class="contentViews"...

Adding banners in other scenarios
---------------------------------

Non-structural folder: put the carousel in the containing folder::

  >>> self.setRoles(['Manager'])
  >>> self.portal.invokeFactory('Folder', 'nonstructural')
  'nonstructural'
  >>> from zope.interface import alsoProvides
  >>> from Products.CMFPlone.interfaces import INonStructuralFolder
  >>> alsoProvides(self.portal.nonstructural, INonStructuralFolder)
  >>> browser.open('http://nohost/plone/nonstructural')
  >>> browser.getLink('Carousel').click()
  >>> browser.url
  'http://nohost/plone/carousel/@@edit-carousel'

Collection, not default item: put the carousel in the collection itself::

  >>> try:
  ...     self.portal.invokeFactory('Topic', 'collection')
  ...     self.portal.default_page = 'collection'
  ... except:
  ...     self.portal.invokeFactory('Collection', 'collection')
  'collection'
  >>> browser.open('http://nohost/plone/collection')
  >>> browser.getLink('Carousel').click()
  >>> browser.url
  'http://nohost/plone/carousel/@@edit-carousel'

Customizing Carousel
====================

It is possible to customize presentation of the Carousel by registering custom
templates for the banner and pager. To simplify the registration of Carousel
templates and their associated menu items, Carousel includes special
ZCML directives. To begin, define the Carousel XML namespace in your product's
configure.zcml::

    xmlns:carousel="http://namespaces.plone.org/carousel"

Then load the ZCML for Carousel::

    <include package="Products.Carousel" />

Finally, register your templates::

    <carousel:banner
      name="banner-example"
      template="banner-example.pt"
      title="Default"
      />

    <carousel:pager
      name="pager-classic"
      template="templates/pager-classic.pt"
      title="Title and Text"
      />

Both the banner and pager directives can also accept a layer attribute to
restrict the availability of the template to a particular browser layer.

To make the development of banner and pager templates less repetitive,
Carousel includes macros in the banner-base and pager-base templates. See
banner-default.pt and pager-titles.pt for examples of how to use these macros.


Carousel Events
===============

Carousel triggers jQuery events at key points in its operation, making it
possible to integrate Carousel with other interactive elements on the page.
These events are triggered on the Carousel container element:

afterAnimate
    Triggered immediately before animation begins. It passes as parameters the
    Carousel object, the index of the previous banner and the index of the
    current banner.

beforeAnimate
    Triggered immediately before animation begins. It passes as parameters the
    Carousel object, the index of the current banner and the index of the
    banner that will be active at the end of the animation.

pause
    Triggered when animation is paused, such as when the user mouses over
    the Carousel. It passes as its parameter the Carousel object.

play
    Triggered when animation begins or resumes. It passes as its parameter the
    Carousel object.

The Carousel object, which is passed as the first optional parameter to event
handlers, is a Javascript object that encapsulates the current state of the
Carousel. See carousel.js for details of the Carousel object.

To bind a callback to one of the Carousel events, select the Carousel container
element and call the jQuery bind method on it::

    (function ($) {
        $('.carousel').bind('afterAnimate',
            function (event, carousel, old_index, new_index) {
            console.log(carousel);
            console.log(old_index);
            console.log(new_index);
        });
    })(jQuery);

Tests
=======

To run tests see ``.travis.yml``.

Making a release
=================

Do with `zest.releaser <http://opensourcehacker.com/2012/08/14/high-quality-automated-package-releases-for-python-with-zest-releaser/>`_

Example::

    # Install zest.releaser in venv and activate that venv
    fullrelease


Support
=========

- Use stackoverlow.com for usage and development related questions

- File bugs and patches at `Github project <https://github.com/collective/Products.Carousel>`_

