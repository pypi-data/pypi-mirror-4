mysolr
======

Fast python solr binding. Check full documentation here_

Status
------

.. image:: https://secure.travis-ci.org/RedTuna/mysolr.png
   :target: https://secure.travis-ci.org/RedTuna/mysolr

Features
--------

* Full query syntax support
* Facets support
* Highlighting support
* Spellchecker support
* More like this support
* Stats support
* Concurrent searchs
* Python 3 compatible


Installation
------------

From source code: ::

  python setup.py install

From pypi: ::

  pip install mysolr


Usage
-----
::

  from mysolr import Solr

  # Default connection to localhost:8080
  solr = Solr()

  # All solr params are supported!
  query = {'q' : '*:*', 'facet' : 'true', 'facet.field' : 'foo'}
  response = solr.search(**query)

  # do stuff with documents
  for document in response.documents:
      # modify field 'foo'
      document['foo'] = 'bar'

  # update index with modified documents
  solr.update(response.documents, commit=True)


.. _here: http://mysolr.redtuna.org
