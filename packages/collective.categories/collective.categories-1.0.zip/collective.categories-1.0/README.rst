Introduction
============

Categories are not tags. Categories allowed for a broad grouping of post topics.
They can be hierarchical but you should not have that much categories.

This addon add a field categories to all content types based on archetypes
and in the portal_catalog to be able to do search based on categories.

Features
========

You can add categories to your content.

Pluggable backend. This addon by default use the same storage and widget
as the tags keyword. But you can install and configure extra storage / widget.

Configure the backend using the registry configlet or in a profile as follow::

    <record name="collective.categories.backend">
        <value>archetypes.linguakeywordwidget</value>
        <!-- or Products.ATVocabularyManager-->
    </record>

Products.ATVocabularyManager
----------------------------

Using Products.ATVocabularyManager, you can add tree vocabularies
for your categories. You have in this case to create a 'collective.categories'
vocabulary in the configlet of the vocabulary manager

And if you add Products.LinguaPlone to ATVocabularyManager you can also make
your vocabulary multilingual !

archetypes.linguakeyword
------------------------

This backend add support to multilingual categories but use default Plone
LinesField for storage.

If you use this backend you should check the skin directories order because
they both override the script collectKeyword.py. 'linguakeywordwidget'
skin directory should be before the 'collective_categories' one.


How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

You have two optional dependencies:

* [Products.ATVocabularyManagaer]
* [archetypes.linguakeywordwidget]

Credits
=======

Companies
---------

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. _sitemap: http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668&topic=8476&ctx=topic
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
