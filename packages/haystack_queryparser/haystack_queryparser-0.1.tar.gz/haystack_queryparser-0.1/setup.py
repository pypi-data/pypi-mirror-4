from distutils.core import setup

long_description="""
haystack-queryparser
====================

Converts arbitrarily complicated user entered query strings to a haystack query object.

###Usage
  ```python
  from haystack_queryparser import ParseSQ
  ```
  Also provides or_parser and and_parser which can be directly used with a query
  ```python
  parser = ParseSQ() 
  sq_object = parser.parse(query)
  ```
  takes a `AND` or `OR` operator to use as default optionally.

###Input
  Input should be a string.This the query.
  
###Output
  Output is a `SQ(haystack.query.SQ)` object.
  This can be passed to `SearchQuerySet.filter` and the	query will be applied

###Test
  To run the test you need to be in the django environment.So you can do something like this:
```
$ python manage.py shell
>>> import haystack_queryparser.tests as test
>>> tests.main()
test_operators (modules.haystack_queryparser2.tests.SimpleTest) ... ok
test_parse (modules.haystack_queryparser2.tests.SimpleTest) ... ok
test_parse_with_new_default (modules.haystack_queryparser2.tests.SimpleTest) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.004s

OK
```
"""

setup(name='haystack_queryparser',
      version='0.1',
      description='A search query parser that works in conjunction with haystack',
      long_description = long_description,
      author='Vignesh Sarma K',
      author_email='vignesh@recruiterbox.com',
      url='https://github.com/recruiterbox/haystack-queryparser',
      classifiers = [
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      ],
      keywords = ["parsing", "query", "search"],
      packages = ['haystack_queryparser'],
      )
