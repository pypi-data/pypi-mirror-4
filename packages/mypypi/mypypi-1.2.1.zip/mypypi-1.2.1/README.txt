======
README
======

This package provides a private python package index server based on Zope 3.

The MyPyPi server provides everything you need for setup a private or public
pypi mirror. It also allows to release closed source packages. Together with
lovely.buildouthttp you can setup a secure pypi mirror which you can use
for your deploy management of public and private packages. Private packages can
get protected by security based on groups, roles and users. The mypypi server
supports a secure way to mix private and public packages at the same time.

We recommend to install the mypypi server behind an apache proxy for SSL
offload like any other SSL secured zope application. But if you like to use a
very simple setup without SSL, the mypypi server should work on port 80 as a
standalone application server as well.


Install
-------

The installation process is very simple and described in the INSTALL.txt file.


Usage
-----

Since version 1.1.0, there is a simpler concept for use the mypypi server as
an index or for register/upload packages. In previous versions we had to use
some undocumented apache rewrite rules. Let's first give an overview what 
a pypi server is use for:

distutils -- can register and upload new packages

setuptools -- can register and upload new packages

easy_install -- downloads packages starting at a given index

zc.buildout -- downloads packages starting at a given index

mypypi -- can mirror packages from another mypypi server using XML-RPC

xmlrpclib -- can access a defined API, http://wiki.python.org/moin/CheeseShopDev 

urllib --  can GET or POST data


In general we use a pypi server for 3 different tasks.

1. as index server for package download (index)

3. register and upload new packages (manage)

3. introspect for additional package information (introspect)

The mypypi server provides the following pages and methods at the root, e.g.
http://host:port

/ -- the distutils and setuptools API methods using GET and POST requests

/ -- the XML-RPC API methods used for get detailed package and release
  information, see http://wiki.python.org/moin/CheeseShopDev

/simple -- used as PUBLIC python package index page. Note, only public
  accessiible packages get listed in this index without authentication
  
/private -- used as THE python package index for projects with protected
  packages. Using this index requires authentication (recommended)

/eggs -- a simpler python package index page listing all release files without
  a page for each project (not recommended for large indexes)


Other important pages are available at:

/ -- mypypi application root offering the mypypi management. This mypypi root
  also offers the distutils, setuptools and xmlrpc APi methods as described
  above 

/pypi -- list the 50 newest packages, inncluding batching

/++projects++ -- supports a (WebDAV) buildout container like used in
  keas.build, see http://pypi.python.org/pypi/keas.build form ore information


Authentication
--------------

The authentication is done implicit in each tool. This means you don't have to
include the authentication (e.g. username:password#host:port/page) in any url.
This means all tools like distutil, setuptools will use the ``.pypirc`` file
for authentication. The mypypi server uses for it's XML-RPC client this
``.pypirc`` too. You only need this file for mypypi if you like to mirror 
a private pypi index server whihc requires authentication.


HTTPS
-----

Distutils and setuptools do not offer SSL support for any method they use.
I do not know how someone can implement an API using SSL and non SSL. But this
is how it is. It is possible run a working mypypi server only on an HTTPS port.
The important methods register, upload will use a https url but the 
list-classifiers and verify options do not support using https.


Release
-------

After you have a working MyPyPi server setup, you have to configure your
projects if you like to have real protection. We use an enhanced setup.py
file in our packages which will prevent a release to pypi.python.org. Such
a setup.py change will also make the release process easier. There are two
option described below for bind a release process to a given repository.


setup.py (version 1)
~~~~~~~~~~~~~~~~~~~~

Since we can use more then one server setup data in the ``.pypirc`` file, we
use this file as our base for bind release process to a given repository.

Note, this allows to bind the release to a server by it's name and requires
that every developer which can release such a package has to use the same
server - repository mapping in it's .pypirc file!

The changed setup.py in your private egg should look like::

  ###############################################################################
  #
  # Copyright 2009 by Projekt01 GmbH , CH-6330 Cham
  #
  ###############################################################################
  """Setup for smart package

  $Id: setup.py 4820 2009-05-12 07:31:00Z adam.groszer $
  """
  #---[ START Server locking]--------------------------------------------------

  LOCK_PYPI_SERVER = "http://pypi.your-domain.tld/eggs"

  import os
  import sys
  from setuptools import setup, find_packages

  def read(*rnames):
      return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

  #---[ repository locking ]-----------------------------------------------------
  
  REPOSITORY = "myserver"
  
  def checkRepository(name):
      server = None
      # find repository in .pypirc file
      rc = os.path.join(os.path.expanduser('~'), '.pypirc')
      if os.path.exists(rc):
          config = ConfigParser()
          config.read(rc)
          if 'distutils' in config.sections():
              # let's get the list of servers
              index_servers = config.get('distutils', 'index-servers')
              _servers = [s.strip() for s in index_servers.split('\n')
                          if s.strip() != '']
              for srv in _servers:
                  if srv == name:
                      repos = config.get(srv, 'repository')
                      print "Found repository %s for %s in '%s'" % (
                          repos, name, rc)
                      server = repos
                      break
  
      if not server:
          print "No repository for %s found in '%s'" % (name, rc)
          sys.exit(1)
  
      COMMANDS_WATCHED = ('register', 'upload')
      changed = False
  
      for command in COMMANDS_WATCHED:
          if command in sys.argv:
              #found one command, check for -r or --repository
              commandpos = sys.argv.index(command)
              i = commandpos+1
              repo = None
              while i<len(sys.argv) and sys.argv[i].startswith('-'):
                  #check all following options (not commands)
                  if (sys.argv[i] == '-r') or (sys.argv[i] == '--repository'):
                      #next one is the repository itself
                      try:
                          repo = sys.argv[i+1]
                          if repo.lower() != server.lower():
                              print "You tried to %s to %s, while this package "\
                                     "is locked to %s" % (command, repo, server)
                              sys.exit(1)
                          else:
                              #repo OK
                              pass
                      except IndexError:
                          #end of args
                          pass
                  i=i+1
  
              if repo is None:
                  #no repo found for the command
                  print "Adding repository %s to the command %s" % (
                      server, command )
                  sys.argv[commandpos+1:commandpos+1] = ['-r', server]
                  changed = True
  
      if changed:
          print "Final command: %s" % (' '.join(sys.argv))
  
  checkRepository(REPOSITORY)
  
  #---[ repository locking ]-----------------------------------------------------

  setup(
      name='smart',
      version = '1.0.0',
      url='http://pypi.your-domain.tld',
      license='commercial',
      description='Be smart',
      author='Adam Groszer, Roger Ineichen',
      author_email='dev@your-domain.tld',
      long_description='\n\n'.join([
          open('README.txt').read(),
          open('CHANGES.txt').read(),
          ]),
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.jsonrpc',
            'z3c.testing',
            'zope.testing',
            ],
        ),
      install_requires=[
        'setuptools',
        'zope.interface',
       ],
      include_package_data = True,
      zip_safe = False,
  )

As you can see we lock the server to a given server name within the line::

  REPOSITORY = "myserver"

The real repository url for the given server name must be available in your
.pypirc file located in your HOME directory and looks like:

  [distutils]
  index-servers = pypi
                  localhost
                  myrepos
  
  [pypi]
  repository: http://pypi.python.org/pypi
  username:your-username
  password:your-password
  
  [localhost]
  repository: http://localhost:8080
  username:your-username
  password:your-password
  
  [myrepos]
  repository: http://localhost:8080
  username:your-username
  password:your-password

After doing the above changes to your setup.py file, you can issue::

  python setup.py register sdist upload

or just::

  python setup.py sdist upload

The lock method will ensure that the repository only get released to the right
repository and prevents that the egg get published by accident to the official
pypi.python.org server at any time.


setup.py (version 2)
~~~~~~~~~~~~~~~~~~~~

The following concept uses a full url pointing to a pypi server. If you don't
like to nail down the full repository url because of legacy data problems,
use the concept described above. The changed setup.py in your private egg
should look like::

  ###############################################################################
  #
  # Copyright 2009 by Projekt01 GmbH , CH-6330 Cham
  #
  ###############################################################################
  """Setup for smart package

  $Id: setup.py 4820 2009-05-12 07:31:00Z adam.groszer $
  """
  #---[ START Server locking]--------------------------------------------------

  LOCK_PYPI_SERVER = "http://pypi.your-domain.tld/eggs"

  import os
  import sys
  from setuptools import setup, find_packages

  def read(*rnames):
      return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

  def check_server(server):
      if not server:
          return

      COMMANDS_WATCHED = ('register', 'upload')

      changed = False

      for command in COMMANDS_WATCHED:
          if command in sys.argv:
              #found one command, check for -r or --repository
              commandpos = sys.argv.index(command)
              i = commandpos+1
              repo = None
              while i<len(sys.argv) and sys.argv[i].startswith('-'):
                  #check all following options (not commands)
                  if (sys.argv[i] == '-r') or (sys.argv[i] == '--repository'):
                      #next one is the repository itself
                      try:
                          repo = sys.argv[i+1]
                          if repo.lower() != server.lower():
                              print "You tried to %s to %s, while this package "\
                                     "is locked to %s" % (command, repo, server)
                              sys.exit(1)
                          else:
                              #repo OK
                              pass
                      except IndexError:
                          #end of args
                          pass
                  i=i+1

              if repo is None:
                  #no repo found for the command
                  print "Adding repository %s to the command %s" % (
                      server, command )
                  sys.argv[commandpos+1:commandpos+1] = ['-r', server]
                  changed = True

      if changed:
          print "Final command: %s" % (' '.join(sys.argv))

  check_server(LOCK_PYPI_SERVER)

  #---[ END Server locking]----------------------------------------------------

  setup(
      name='smart',
      version = '1.0.0',
      url='http://pypi.your-domain.tld',
      license='commercial',
      description='Be smart',
      author='Adam Groszer, Roger Ineichen',
      author_email='dev@your-domain.tld',
      long_description='\n\n'.join([
          open('README.txt').read(),
          open('CHANGES.txt').read(),
          ]),
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      extras_require = dict(
        test = [
            'z3c.coverage',
            'z3c.jsonrpc',
            'z3c.testing',
            'zope.testing',
            ],
        ),
      install_requires=[
        'setuptools',
        'zope.interface',
       ],
      include_package_data = True,
      zip_safe = False,
  )

As you can see we lock the server to a given URL within the line::

  LOCK_PYPI_SERVER = "http://pypi.your-domain.tld/eggs"

After doing the above changes to your setup.py file, you can issue::

  python setup.py register sdist upload

or just::

  python setup.py sdist upload

The lock method will ensure that the repository only get released to the right
repository and prevents that the egg get published by accident to the official
pypi.python.org server at any time.


buildout.cfg
~~~~~~~~~~~~

Since we use a HTTPS connection, we have to improve our buildout.cfg file and
use the lovely buildouthttp recipe which enables SSL support. See
lovely.buildouthttp for more information about this recipe. Also make sure
you setup the required information like described in the lovely recipe if you
use the recipe the first time.

You private egg buildout.cfg should look like::

  [buildout]
  index = https://pypi.your-domain.tld/private
  extensions = lovely.buildouthttp
  extends = http://download.zope.org/zope3.4/3.4.0/versions.cfg
  prefer-final = true
  versions = versions
  develop = .
  parts = test

  [test]
  recipe = zc.recipe.testrunner
  eggs = smart [test]

As you can see, our mypypi server is used as the index. We use the private
page at https://pypi.your-domain.tld/private because this page forces the
urllib handler to use the basic auth realm authentication. Again; note this
requires a working lovely.buildouthttp setup using a .httpauth file in your
HOME folder. Such a .httpauth file looks like::

  pypi,https://pypi.your-domain.tld,your-login,your-password

Note the realm is always pypi. This is defined at the serverside and could
not get changed. Of course could we change the realm in our mypypi server, but
since ``setuptools`` uses this hardcoded realm (eeek), buildout upload would
not work anymore if we would change the realm to something else. Let us know
if this will become a real problem for you.


Contact
-------

Sorry about this minimal documentation. But if you have any questions or
if you like to help improve the documentation, feel free to contact us at
<dev at projekt01 - ch>
