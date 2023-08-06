wpd.countdown
*************

Overview
--------

A portlet to display a countdown to the World Plone Day.

Requirements
------------

This product works with Plone 4.x


Installation
------------

To enable this product,on a buildout based installation:

Edit your buildout.cfg and add ``wpd.countdown``
to the list of eggs to install ::

    [buildout]
    ...
    eggs =
        wpd.countdown

After updating the configuration you need to run the ''bin/buildout'',
which will take care of updating your system.

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product (check its checkbox) and click the 'Install' button.


Development
-----------

Development of this product was done by:

* `Simples Consultoria <http://www.simplesconsultoria.com.br/>`_
* `Starzel.de <http://www.starzel.de/>`_


Credits
-------

* Philip Bauer (pbauer at starzel.de) - Packaging, review, documentation

* Steffen Lindner (mail at steffen-lindner.de) - Update to Version 2

* Andre Nogueira (andre at simplesconsultoria.com.br) - Idea, layout

* Davi Lima (davilima at simplesconsultoria.com.br) - Idea,
  planning and lines of code

* Erico Andrei (erico at simplesconsultoria.com.br) - Packaging, i18n

