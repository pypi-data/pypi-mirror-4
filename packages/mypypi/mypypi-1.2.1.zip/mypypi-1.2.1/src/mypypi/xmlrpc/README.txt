======
README
======

The mypypi server provides since version 1.1.0 an XML-RPC APi like given from
the original pypi.python.org server. For More information see:
http://wiki.python.org/moin/PyPiXmlRpc?action=show&redirect=CheeseShopXmlRpc


PYPIProxy
---------

Let's use our PYPIProxy for connect to ourself.

  >>> from zope.app.testing.xmlrpc import ServerProxy
  >>> pypiProxy = ServerProxy('http://mgr:mgrpw@localhost/')
  >>> pypiProxy
  <ServerProxy for mgr:mgrpw@localhost/>


the mypypi offers different methods for retrive package and release data. Let's
show the different methods:


list_packages
-------------

Retrieve a list of the package names registered with the package index. Returns
a list of name strings.

  >>> pypiProxy.list_packages()
  []


package_releases
----------------

Retrieve a list of the releases registered for the given package name. Returns
a list of version strings.

  >>> packageName = 'z3c.form'
  >>> pypiProxy.package_releases(packageName)
  []

As you can see the above method returns only one singel version. There is an
option called ``show_hidden`` which will allow to show all release versions:

  >>> packageName = 'z3c.form'
  >>> show_hidden = True
  >>> pypiProxy.package_releases(packageName, show_hidden)
  []


release_urls
------------

Retrieve a list of download URLs for the given package release. Returns a list
of dicts with the following keys:

- url

- packagetype ('sdist', 'bdist', etc)

- filename

- size

- md5_digest

- downloads

- has_sig

- python_version (required version, or 'source', or 'any')

- comment_text

  >>> version = '1.9.0'
  >>> pypiProxy.release_urls(packageName, version)
  []


release_data
------------

Retrieve metadata describing a specific package release. Returns a dict with
keys for:

- name

- version

- stable_version

- author

- author_email

- maintainer

- maintainer_email

- home_page

- license

- summary

- description

- keywords

- platform

- download_url

- classifiers (list of classifier strings)

  >>> packageName = 'z3c.authenticator'
  >>> version = '0.5.0'
  >>> pypiProxy.release_data(packageName, version)
  {}


search
------

Not implemented yet!

Search the package database using the indicated search spec. The spec may
include any of the keywords described in the above list
(except 'stable_version' and 'classifiers'), for example:

{'description': 'spam'}

will search description fields. Within the spec, a field's value can
be a string or a list of strings (the values within the list are
combined with an OR), for example:

{'name': ['foo', 'bar']}.

Arguments for different fields are combined using either "and"
(the default) or "or". Example:

search({'name': 'foo', 'description': 'bar'}, 'or').

The results are returned as a list of dicts:

pypiProxy.search({'name': 'z3c.form', 'version': '1.9.0'}, 'and')


changelog
---------

Not implemented yet!

Retrieve a list of four-tuples (name, version, timestamp, action) since the
given timestamp. All timestamps are UTC values. The argument is a UTC integer
seconds since the epoch.

from time import time
since = int(time() - 60)
pypiProxy.changelog(since)
