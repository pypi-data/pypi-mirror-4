Documentation
=============

Yet another multimedia/dynamic portlet for Plone that display images.

Why you can want this instead of other? Because it works with Javascript disabled (with an eye
onto the `Italian Accessibility Act`__) and is tested to work behind reverse-proxy (like
`Varnish`__).

__ http://www.pubbliaccesso.it/normative/DM080705-A-en.htm
__ http://varnish-cache.org/

.. figure:: http://keul.it/images/plone/auslfe.portlet.multimedia-0.2.0.png
   :alt: Portlet preview
   
   How the portlet looks like on AUSL web site

How to use
----------

The main information you must provide to the portlet is a Plone collection. The collection is
used to retrieve all image-like contents from it. You can freely configure the collection to
return also other content, but only ones marked as "image-able" are used (technically speaking:
it also filter only contents that provides *IImageContent*, like "Image" and "News Item" content
type already do).

From the target collection is also used the "*Number of items*" field, to show in the portlet only
a limited number of images.

The "*Limit Search Results*" field is not directly used by this portlet, but change the collection
behaviour. Enabling the client random feature with this check selected will only reorder a limited
set of images.

Performance
-----------

What scare us about other Javascript-live multimedia portlet (besides accessibility) is the massive
use of AJAX call to the server. This can lead to two problems:

* too many request (and low performance)
* random feature could work badly with cache in front of Plone

For this reason this portlet will not query every *xyz* seconds the server, but simply get from
the server all the images, then randomly reload them client side.

The *auto-reload feature* can be disabled if you don't like it. You still have a random image
set at page load time.

Translations
------------

When using client side reload feature, the user can (for accessibility reason) stop and restart the
auto-reload task.

The portlet title will display an help message. To add additional translation you are able to *not*
change the product source.

Just add something like this in one of your Javascript source::

    jQuery.auslfe_multimedia = {
        i18n: {
            xx: {
                stopReload: '"Click to stop auto-reload" in xx language',
                restartReload: '"Click to restart auto-reload" in xx language'
            }
        }
    };

Change *xx* above with the 2-letters code of your language and customize other strings.
Language loaded is taken from the language of the site (for any problem, fallback on english).


Credits
=======

Developed with the support of `Azienda USL Ferrara`__; Azienda USL Ferrara supports the
`PloneGov initiative`__.

.. image:: http://www.ausl.fe.it/logo_ausl.gif
   :alt: Azienda USL's logo

__ http://www.ausl.fe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

