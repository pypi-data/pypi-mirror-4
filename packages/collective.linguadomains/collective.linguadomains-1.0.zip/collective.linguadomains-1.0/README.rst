Introduction
============

This addon let you manage translated domains and redirect user to correct
domain according to negotiated language.

How to install
==============

You can install this addon as any other Plone addons. Please follow official
documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to

This addon depends on Products.LinguaPlone

How to use
==========

Once the addon is installed you have a controlpanel where you can configure
each url for languages. Be warned no redirection happens if the url is not
configured.

Example::

    http://en.example.be|en
    http://stagingen.example.be|en
    http://deven.example.be|en
    http://nl.example.be|nl
    http://stagingnl.example.be|nl
    http://devnl.example.be|nl
    http://fr.example.be|fr
    http://stagingfr.example.be|fr
    http://devfr.example.be|fr

IMPORTANT: The choice is based on the order.

You can also configure using registry.xml in your generic setup profile::

  <records interface="collective.linguadomains.interfaces.ISettingsSchema">
     <value key="activated">True</value>
     <value key="mapping">
        <element>http://fr.example.be|fr</element>
        <element>http://stagingfr.example.be|fr</element>
        <element>http://devfr.example.be|fr</element>

        <element>http://nl.example.be|nl</element>
        <element>http://stagingnl.example.be|nl</element>
        <element>http://devnl.example.be|nl</element>

        <element>http://en.example.be|en</element>
        <element>http://stagingen.example.be|en</element>
        <element>http://deven.example.be|en</element>
     </value>
  </records>

Credits
=======

Companies
---------

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact Makina-Corpus <mailto:python@makina-corpus.org>`_

Contributors
------------

- author: JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>


.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. _sitemap: http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668&topic=8476&ctx=topic
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
