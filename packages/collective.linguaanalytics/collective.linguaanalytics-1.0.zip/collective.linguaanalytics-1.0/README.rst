Introduction
============

This addon override collective.googleanalytics to support translated domains.

It can also be used in the case you don't want to use oauth binding between
Plone and Google Analytics but just configure the code.


How to use
==========

Once the addon is installed you have a controlpanel where you can configure
each url for languages. Be warned no redirection happens if the url is not
configured.

Example::

    http://www.brussels.irisnet.be|UA-XXXXX-Y
    http://www.brussel.irisnet.be|UA-YYYYY-Z
    http://www.bruxelles.irisnet.be|UA-ZZZZZ-X

Credits
=======

Companies
---------

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact Makina-Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. _sitemap: http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668&topic=8476&ctx=topic
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
