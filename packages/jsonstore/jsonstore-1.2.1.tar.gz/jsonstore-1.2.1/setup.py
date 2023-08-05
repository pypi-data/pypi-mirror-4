from setuptools import setup, find_packages
import sys, os

version = '1.2.1'

setup(name='jsonstore',
      version=version,
      description="JSONStore is a lightweight database for JSON documents exposed through HTTP.",
      long_description="""\
A schema-free database for JSON documents, exposed through a REST API, with searching implemented using a flexible matching algorithm.

A quick start::

    $ pip install jsonstore
    $ jsonstore
     * Running on http://127.0.0.1:31415/

Creating a document::

    $ curl -v http://127.0.0.1:31415/ -d '{"foo":"bar","baz":{"count":42}}'
    < HTTP/1.0 201 Created
    < Location: http://127.0.0.1:31415/72dcf1ee-8efd-4d7f-8ca1-2eda2bf85099
    < etag: "348f16ee0c0856d853117bde8413a4270d1d3487"
    {
        "foo": "bar",
        "baz": {
            "count": 42
        },
        "__id__": "72dcf1ee-8efd-4d7f-8ca1-2eda2bf85099",
        "__updated__": "2012-05-09T20:33:36.928075+00:00"
    }

Searching the store::

    $ curl -g 'http://127.0.0.1:31415/{"baz":{"count":"GreaterThan(40)"}}'
    [
        {
            "foo": "bar",
            "baz": {
                "count": 42
            },
            "__id__": "72dcf1ee-8efd-4d7f-8ca1-2eda2bf85099",
            "__updated__": "2012-05-09T20:33:36.928075+00:00"
        }
    ]

It also has a Python API. The above code would be done like this::

    >>> from jsonstore.client import EntryManager
    >>> from jsonstore.operators import GreaterThan
    >>> em = EntryManager('http://127.0.0.1:31415/')
    >>> em.create(foo="bar", "baz"={"count": 42})
    >>> em.search(baz={"count": GreaterThan(40)})

Please see the website for `more examples <http://code.dealmeida.net/jsonstore>`_.

""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Roberto De Almeida',
      author_email='roberto@dealmeida.net',
      url='http://code.dealmeida.net/jsonstore',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'WebOb',
          'simplejson',
          'uuid',
          'requests>=0.12.1',
          'iso8601',
          'docopt>=0.4.1',
          'SQLAlchemy',
          'Werkzeug',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = jsonstore.rest:make_app

      [console_scripts]
      jsonstore = jsonstore.run:main
      """,
      )
      
