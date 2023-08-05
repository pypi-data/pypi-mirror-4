Introduction
============

The piece of software that make it possible to sort items in Plone contains hidden additional features.

Normally, when you call a sort action in Plone, you call a URL like this::

    http://myhost/myfolder/folder_position?position=up&id=content_id

... of course, KSS/jQuery stuff in recent Plone versions will hide this feature, but is still available when you disable
Javascript.

The Plone UI has no way at the moment for performing actions like this::

    http://myhost/myfolder/folder_position?position=ordered&id=fieldname

But this feature is inside Plone: in this way you will sort a folder automatically, using a field value for comparison
(like "*title*", or "*created*").

The *folder_position* script uses the *orderObjects* API. This last method has some additional nice features that
unluckily are not exposed to users. But we can fix this.

What this product does
======================

This product adds to Plone some of the features that follow, patching Plone a little (see also `#11317`__).

__ http://dev.plone.org/plone/ticket/11317

Can now sort a folder in reverse order
--------------------------------------

You can call an URL like this::

    http://myhost/myfolder/folder_position?position=ordered&id=created&reverse=1

and this will sort the folder using reverse criteria.

Add "delta" criteria to the sorting mechanism
---------------------------------------------

You can call::

    http://myhost/myfolder/folder_position?position=up&id=content_id&delta=4

and this will move the content down by 4 slots instead of the default 1 (this feature is not so useful if you use Plone KSS/jQuery/Javascript
sorting).

Add a nice Plone interface for global folder sorting
----------------------------------------------------

Your "*Action*" menu will be populated with a new entry: "*Sort folder*". This will present the user a Plone form where
he can perform common sorting operations.

.. image:: http://keul.it/images/plone/collective.sortmyfolder-1.0.0.png
   :alt: Sort my folder form

The last option makes it possible for users to specify a custom attribute that's not in the list; if you don't like this,
just add a CSS rules which hides the ``choice_custom_field`` element. Use of this last option needs some Javascript to
be executed.

What this product isn't
=======================

This product only reveals features that are already in Plone (inside the *orderObjects* method).
It will not add new sorting behaviour.

Dependencies
============

Testing for collective.sortmyfolder has been done on:

* Plone 3.3
* Plone 4.0 

Credits
=======

Developed with the support of `S. Anna Hospital, Ferrara`__; S. Anna Hospital supports the
`PloneGov initiative`__.

__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

 