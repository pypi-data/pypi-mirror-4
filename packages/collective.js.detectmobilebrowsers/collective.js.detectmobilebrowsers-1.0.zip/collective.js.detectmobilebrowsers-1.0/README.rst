Introduction
============

This addon register a modified version of detectmobilebrowsers_ to give
a isMobile javascript variable so you can play around with javascript.

version: 18 October 2012 (check the footer of detectmobilebrowsers_)

How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

The javascript is registred in a bundle so you will have to configure your theme
to use it this way::

    <registry>
      <record name="Products.ResourceRegistries.interfaces.settings.IResourceRegistriesSettings.resourceBundlesForThemes">
        <value>
          <element key="plonetheme.mytheme">
            <element>default</element>
            <element>detectmobilebrowsers</element>
          </element>
        </value>
      </record>
    </registry>


Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
.. _detectmobilebrowsers: http://detectmobilebrowsers.com/
