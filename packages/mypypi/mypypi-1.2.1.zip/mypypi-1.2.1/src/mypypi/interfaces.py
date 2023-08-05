##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.location.interfaces
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.container.interfaces import IContainer, IContained
from zope.container.constraints import containers
from zope.container.constraints import contains
from zope.site.interfaces import IRootFolder

import z3c.schema.email
from z3c.authenticator.interfaces import IUser
from z3c.authenticator.interfaces import IGroup

from p01.remote.interfaces import IRemoteProcessor
from p01.remote.interfaces import IJob

import p01.fsfile.interfaces

from mypypi.i18n import MessageFactory as _

LOG_CONTAINER_KEY = u'mypypi.interfaces.ILogContainer'
LOGGER_KEY = u'mypypi.interfaces.ILogger'
PROJECT_CONTAINER_KEY = u'mypypi.interfaces.IProjectContainer'
PUBLIC_CONTAINER_KEY = u'mypypi.interfaces.IPublicContainer'


# authentication
class IPYPIUser(IUser):
    """PYPI server user."""

    lastName = zope.schema.TextLine(
        title=_(u'Last Name'),
        description=_(u'The last name of the testee.'),
        required=True)

    firstName = zope.schema.TextLine(
        title=_(u'First Name'),
        description=_(u'The first name of the testee.'),
        required=True)

    email = z3c.schema.email.field.RFC822MailAddress(
        title=_(u'Email'),
        description=_(u'The email address.'),
        required=True)

    phone = zope.schema.TextLine(
        title=_(u'Phone'),
        description=_(u'The phone number.'),
        required=False)

class IPYPIAdmin(IPYPIUser):
    """PYPI adminstration user."""


class IPYPIGroup(IGroup):
    """PYPI server group."""

    __name__ = zope.schema.ASCIILine(
        title=u'Group Name',
        description=u'Group Name',
        required=True)

    title = zope.schema.TextLine(
        title=_("Group Title"),
        description=_("Provides a title for the group."),
        required=True)

    description = zope.schema.Text(
        title=_("Group Description"),
        description=_("Provides a description for the group."),
        required=False)


# site
class IPYPISite(IRootFolder, IRemoteProcessor, IAttributeAnnotatable):
    """Pypi application root folder."""
    contains('mypypi.interfaces.IPackage')

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the buildout package server.'),
        default=u"PYPISite",
        required=True)

    autoStartMirrorScheduler = zope.schema.Bool(
        title=_(u'Autostart Mirror Scheduler'),
        description=_(u'Autostart Mirror Scheduler.'),
        default=False,
        required=False)

    checkClassifiersOnVerify = zope.schema.Bool(
        title=_(u'Raise error for wrong classifiers on verify'),
        description=_(u'Raise error for wrong classifiers on verify '
                       '(python setup.py upload register --dry-run)'),
        default=True)

    checkClassifiersOnUpload = zope.schema.Bool(
        title=_(u'Raise error for wrong classifiers on upload'),
        description=_(u'Raise error for wrong classifiers on upload '
                       '(python setup.py sdist upload)'),
        default=True)

    packageSynchronizerInterval = zope.schema.Int(
        title=_('Package synchronizer interval'),
        description=_('The interval which the package get synchrnoized. (0=none).'),
        default=1*60*60*24, # daily
        min=60, # we do not allow to set values below one hour
        missing_value=None,
        required=False)

    def syncMirrorPackages():
        """Update all packages and fetch new releases."""

    def getStartTime():
        """Return time the application started in seconds since the epoch."""

    # PYPI API (used in XML-RPC)
    def getPackages():
        """Returns a list of accessible packages"""

    def getReleases(pkgName, showHidden=False):
        """Returns a list of accessible releases"""

    def getRelease(pkgName, version):
        """Returns an accessible release"""

    def getReleaseFiles(pkgName, version):
        """Returns a list of accessible release files"""


class ISyncMirrorPackages(IJob):
    """Job which can start the mirror process."""


class IPublishable(zope.interface.Interface):
    """Publish API."""

    published = zope.schema.Bool(
        title=_(u'Published'),
        description=_(u'Published'),
        default=True)

    isPublished = zope.schema.Bool(
        title=_(u'Is published'),
        description=_(u'Is published'),
        default=False,
        readonly=True)


class ILogContainer(IContainer, IAttributeAnnotatable):
    """Log container."""
    contains('mypypi.interfaces.ILogger')

    def add(comment):
        """Add a log entry based on a comment."""


class ILogger(IContainer, IAttributeAnnotatable):
    """Logger entity."""
    containers(ILogContainer)
    contains('mypypi.interfaces.IHistoryEntry', 'mypypi.interfaces.IErrorEntry')

    userName = zope.schema.Text(
        title=_(u'Username'),
        description=_(u'Username'),
        default=u'',
        required=False)

    def logHistory(message, path=None):
        """Add a new history entry based on the given message and optional path.
        """

    def logError(message, path=None):
        """Add a new error entry based on the given message and optional path.
        """


class ILocalLogger(ILogger):
    """Local logger marker."""


class IMirrorLogger(ILogger):
    """Mirror logger marker."""


class IHistoryEntry(IAttributeAnnotatable):
    """History entry."""
    containers(ILogger)

    message = zope.schema.Text(
        title=_(u'Message'),
        description=_(u'Message'),
        missing_value=u'',
        default=u'',
        required=True,)

    path = zope.schema.TextLine(
        title=_(u'Path'),
        description=_(u'The path from where the source is coming from.'),
        default=u'',
        required=False)


class IErrorEntry(IAttributeAnnotatable):
    """Error entry."""
    containers(ILogContainer)

    message = zope.schema.Text(
        title=_(u'Message'),
        description=_(u'Message'),
        missing_value=u'',
        default=u'',
        required=True,)

    path = zope.schema.TextLine(
        title=_(u'Path'),
        description=_(u'The path from where the source is coming from.'),
        default=u'',
        required=False)


class IPackage(IContainer, IPublishable, IAttributeAnnotatable):
    """Package name interface used for define permissions."""


class ILocalPackage(IPackage):
    """Private package representations."""

    containers(IPYPISite)
    contains('mypypi.interfaces.IRelease')

    __name__ = zope.schema.ASCIILine(
        title=_(u'Package Name'),
        description=_(u'Package Name'),
        default='z3c.authenticator',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    latest = zope.interface.Attribute('Pointer to release with highest version')


class IMirrorPackage(IPackage):
    """Pypi package representations."""

    containers(IPYPISite)
    contains('mypypi.interfaces.IRelease')

    __name__ = zope.schema.ASCIILine(
        title=_(u'Package Name'),
        description=_(u'Package Name'),
        default='z3c.authenticator',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    latest = zope.interface.Attribute('Pointer to release with highest version')

    pypiURL = zope.schema.URI(
        title=_(u'PyPi URL'),
        description=_(u'PyPi URL'),
        default='http://pypi.python.org/pypi',
        missing_value=u'',
        required=True)

    def getName(name):
        """pypi is sometimes crazy about names, esp. with -/_"""

    def update():
        """Update this package and fetch new releases."""


class IPackageFetcher(zope.interface.Interface):
    """Can fetch a pacakge from pypi or another pypi like site."""

    def get(name, pypiURL):
        """Create and returns a mirror package."""


class IRelease(IPublishable, IAttributeAnnotatable):
    """Package - Release including metadata."""

    containers(IPackage)

    __name__ = zope.schema.ASCIILine(
        title=_(u'Version'),
        description=_(u'Version'),
        default='0.5.0',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    author = zope.schema.TextLine(
        title=_(u'Author'),
        description=_(u'Author'),
        default=u'',
        required=False)

    authorEmail = zope.schema.TextLine(
        title=_(u'Author Email'),
        description=_(u'Author Email'),
        default=u'',
        required=False)

    cheesecakeCodeKwaliteeId = zope.schema.Int(
        title=_(u'Cheesecake Code Kwalitee Id'),
        description=_(u'Cheesecake Code Kwalitee Id'),
        default=0,
        required=False)

    cheesecakeDocumentationId = zope.schema.Int(
        title=_(u'Cheesecake Documentation Id'),
        description=_(u'Cheesecake Documentation Id'),
        default=0,
        required=False)

    cheesecakeInstallabilityId = zope.schema.Int(
        title=_(u'Cheesecake Installability Id'),
        description=_(u'Cheesecake Installability Id'),
        default=0,
        required=False)

    classifiers = zope.schema.List(
        title=_(u'Classifiers'),
        description=_(u'Classifiers'),
        value_type=zope.schema.TextLine(
            title=_(u'Classifier'),
            description=_(u'Classifier'),
            required=True
            ),
        default=[],
        required=False)

    # that's the egg long description text, see also summary attribute
    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'Description'),
        default=u'',
        required=False)

    downloadURL = zope.schema.TextLine(
        title=_(u'Download URL'),
        description=_(u'Download URL'),
        required=False)

    homePage = zope.schema.TextLine(
        title=_(u'Homepage'),
        description=_(u'Homepage'),
        required=False)

    keywords = zope.schema.TextLine(
        title=_(u'Keywords'),
        description=_(u'Keywords'),
        default=u'',
        required=False)

    # changed to zope.schema.Text
    # Stuart Bishop uses a full text block as license for pytz which means
    # we will get not only a TextLine,
    # See: http://www.python.org/dev/peps/pep-0241/
    license = zope.schema.Text(
        title=_(u'License'),
        description=_(u'License'),
        default=u'',
        required=False)

    maintainer = zope.schema.TextLine(
        title=_(u'Maintainer'),
        description=_(u'Maintainer'),
        default=u'',
        required=False)

    maintainerEmail = zope.schema.TextLine(
        title=_(u'Maintainer Email'),
        description=_(u'Maintainer Email'),
        default=u'',
        required=False)

    obsoletes = zope.schema.List(
        title=_(u'Obsoletes'),
        description=_(u'Obsoletes'),
        value_type=zope.schema.TextLine(
            title=_(u'Obsolete'),
            description=_(u'Obsolete'),
            required=True
            ),
        default=[],
        required=False)

    pypiHidden = zope.schema.Int(
        title=_(u'Pypi hidden'),
        description=_(u'Pypi hidden'),
        default=1,
        required=False)

    pypiOrdering = zope.schema.Int(
        title=_(u'Pypi ordering'),
        description=_(u'Pypi ordering'),
        default=10,
        required=False)

    platform = zope.schema.TextLine(
        title=_(u'Platform'),
        description=_(u'Platform'),
        default=u'',
        required=False)

    protocolVersion = zope.schema.TextLine(
        title=_(u'Protocol Version'),
        description=_(u'Protocol Version'),
        default=u'',
        required=False)

    provides = zope.schema.List(
        title=_(u'Provides'),
        description=_(u'Provides'),
        value_type=zope.schema.TextLine(
            title=_(u'Provides'),
            description=_(u'Provides'),
            required=True
            ),
        default=[],
        required=False)

    requires = zope.schema.List(
        title=_(u'Requires'),
        description=_(u'Requires'),
        value_type=zope.schema.TextLine(
            title=_(u'Require'),
            description=_(u'Require'),
            required=True
            ),
        default=[],
        required=False)

    stableVersion = zope.schema.TextLine(
        title=_(u'Stable version'),
        description=_(u'Stable version'),
        default=u'',
        required=False)

    # that's the egg description text
    summary = zope.schema.Text(
        title=_(u'Summary'),
        description=_(u'Summary'),
        default=u'',
        required=False)

    # on Local this is ==__name__ on Remote it's filled by the system
    version = zope.schema.TextLine(
        title=_(u'Version'),
        description=_(u'Version'),
        default=u'',
        required=False,
        readonly=True)


class ILocalRelease(IRelease, IContainer):
    """Local release representations."""


class IMirrorRelease(IRelease, IContainer):
    """Mirror release representations."""

    url = zope.schema.URI(
        title=_(u'Source URL'),
        description=_(u'Source URL'),
        readonly=True)

    pypiURL = zope.schema.URI(
        title=_(u'PyPi URL'),
        description=_(u'PyPi URL'),
        default='http://pypi.python.org/pypi',
        readonly=True)

    def update():
        """Update and fetch and add new release files."""


class IReleaseFile(p01.fsfile.interfaces.IFSFile, IPublishable,
    IAttributeAnnotatable):
    """Release file representations."""

    containers(IRelease)

    commentText = zope.schema.Text(
        title=_(u'Comment text'),
        description=_(u'Comment text'),
        default=u'',
        required=False)

    downloads = zope.schema.Int(
        title=_(u'Downloads'),
        description=_(u'Downloads'),
        default=0,
        required=False)

    hasSig = zope.schema.Bool(
        title=_(u'Has sig'),
        description=_(u'Has sig'),
        default=False,
        required=False)

    md5Digest = zope.schema.ASCIILine(
        title=_(u'MD5 Digest'),
        description=_(u'MD5 Digest'),
        required=False)

    packageType = zope.schema.TextLine(
        title=_(u'Package type'),
        description=_(u'Package type'),
        default=u'',
        required=False)

    pythonVersion = zope.schema.TextLine(
        title=_(u'Python Version'),
        description=_(u'Python Version'),
        default=u'',
        required=False)

    size = zope.schema.Int(
        title = _(u'Size'),
        description=_(u'The file size.'),
        default=0,
        required=False)

    url = zope.schema.URI(
        title=_(u'Source URL'),
        description=_(u'Release file URL'),
        required=False)

    def update(data):
        """Update release files data."""

#project stuff
#current usage of the project entities is the storage of buildout cfg files
#
class IProjectContainer(IContainer, IAttributeAnnotatable):
    """Project container."""
    contains('mypypi.interfaces.IProject')

    #def add(comment):
    #    """Add a log entry based on a comment."""


class IProject(IContainer, IContained, IAttributeAnnotatable):
    """A project"""
    containers(IProjectContainer)
    contains('mypypi.interfaces.IProjectFile',
             'mypypi.interfaces.IProjectFileBuildout')

    __name__ = zope.schema.ASCIILine(
        title=_(u'Project Name'),
        description=_(u'Project Name'),
        default='',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        default=u'',
        required=True)

    #userName = zope.schema.Text(
    #    title=_(u'Username'),
    #    description=_(u'Username'),
    #    default=u'',
    #    required=False)
    #
    #def logHistory(message, path=None):
    #    """Add a new history entry based on the given message and optional path.
    #    """
    #
    #def logError(message, path=None):
    #    """Add a new error entry based on the given message and optional path.
    #    """

class IProjectFile(IContained, p01.fsfile.interfaces.IFSFile, IPublishable,
    IAttributeAnnotatable):
    """Release file representations."""

    containers(IProject)

    __name__ = zope.schema.ASCIILine(
        title=_(u'File Name'),
        description=_(u'File Name'),
        default='',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    commentText = zope.schema.Text(
        title=_(u'Comment text'),
        description=_(u'Comment text'),
        default=u'',
        required=False)

    downloads = zope.schema.Int(
        title=_(u'Downloads'),
        description=_(u'Downloads'),
        default=0,
        required=False)

    size = zope.schema.Int(
        title = _(u'Size'),
        description=_(u'The file size.'),
        default=0,
        required=False)

class IProjectFileBuildout(IProjectFile):
    """Special buildout (.cfg) type file"""#project stuff
#current usage of the project entities is the storage of buildout cfg files
#
class IPublicContainer(IContainer, IAttributeAnnotatable):
    """Public container."""
    contains('mypypi.interfaces.IPublic')


class IPublic(IContainer, IContained, IAttributeAnnotatable):
    """A project"""
    containers(IPublicContainer)
    contains('mypypi.interfaces.IPublictFile')

    __name__ = zope.schema.ASCIILine(
        title=_(u'Public Name'),
        description=_(u'Public Name'),
        default='',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        default=u'',
        required=True)

class IPublicFile(IContained, p01.fsfile.interfaces.IFSFile,
    IAttributeAnnotatable):
    """Public file representations."""

    containers(IPublic)

    __name__ = zope.schema.ASCIILine(
        title=_(u'File Name'),
        description=_(u'File Name'),
        default='',
        missing_value=u'',
        required=True,
        readonly=True) # don't allow to modify __name__ -- it breaks

    size = zope.schema.Int(
        title = _(u'Size'),
        description=_(u'The file size.'),
        default=0,
        required=False)


class IPYPIContextForXMLRPC(zope.location.interfaces.ILocation):
    """PYPI index context for XML-RPC methods"""


# view marker
class ISiteManagementPage(zope.interface.Interface):
    """Site management page."""

class IPackageManagementPage(zope.interface.Interface):
    """Package management page."""

class IProjectManagementPage(zope.interface.Interface):
    """Project management page."""

class IProjectFileManagementPage(zope.interface.Interface):
    """Project file management page."""

class IPublicManagementPage(zope.interface.Interface):
    """Public management page."""

class IPublicFileManagementPage(zope.interface.Interface):
    """Public file management page."""

class IHistoryManagementPage(zope.interface.Interface):
    """History management page."""

class IUserManagementPage(zope.interface.Interface):
    """User management page."""

class IGroupManagementPage(zope.interface.Interface):
    """Group management page."""

class IRoleManagementPage(zope.interface.Interface):
    """Role management page."""

class IReleaseManagementPage(zope.interface.Interface):
    """Release management page."""

class IReleaseFileManagementPage(zope.interface.Interface):
    """Release file management page."""

class IPYPIPage(zope.interface.Interface):
    """PyPi index page."""
