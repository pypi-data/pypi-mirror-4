This product will add a `permalink`__ to every supported Plone content. A permalink is a link to the content
that should never change even if you rename or move it.

__ http://en.wikipedia.org/wiki/Permalink

How to use
==========

The default implementation is based on the Plone *resolveuid* feature.
This will not work (and shows anything) for contents without the *plone.uuid* support. You can however 
customize and develop additional adapters for providing permalink for yours types (or customize
the default one).

The new resource will be added to the *document actions* section.

.. image:: http://keul.it/images/plone/collective.permalink-0.1.0.png
   :alt: Permalink preview in a basic Plone site

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

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

