##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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
"""XML-RPC API

"""
__docformat__ = "reStructuredText"

from zope.traversing.browser import absoluteURL


class PYPIAPI(object):
    """XML-RPC API"""

    def __init__(self, context, request):
        self.__parent__ = context
        self.context = context
        self.request = request

    def list_packages(self):
        """Returns a list of accessible package names"""
        return [pkg.__name__
                for pkg in self.context.getPackages()]

    def package_releases(self, package_name, show_hidden=False):
        """Returns a list of accessible release names"""
        return [rel.__name__
                for rel in self.context.getReleases(package_name, show_hidden)]
            
    # deprecated
    def package_urls(self, package_name, version):
        return self.release_urls(package_name, version)

    def release_urls(self, package_name, version):
        data = []
        append = data.append
        for f in self.context.getReleaseFiles(package_name, version):
            url = absoluteURL(f, self.request)
            append({'url': url,
                    'packagetype': f.packageType,
                    'filename': f.__name__,
                    'size': f.size,
                    'md5_digest': f.md5Digest,
                    'downloads': f.downloads,
                    'has_sig': f.hasSig,
                    'python_version': f.pythonVersion,
                    'comment_text': f.commentText})
        return data

    # deprecated
    def package_data(self, package_name, version):
        return self.release_data(package_name, version)

# TODO: implement new attributes
    def release_data(self, package_name, version):
        rel = self.context.getRelease(package_name, version)
        if rel is not None:
            pkg = rel.__parent__
            return {'name': pkg.__name__,
                    'version': rel.__name__,
                    'stable_version': rel.stableVersion,
                    'author': rel.author,
                    'author_email': rel.authorEmail,
                    'maintainer': rel.maintainer,
                    'maintainer_email': rel.maintainerEmail,
                    'home_page': rel.homePage,
                    'license': rel.license,
                    'summary': rel.summary,
                    'description': rel.description,
                    'keywords': rel.keywords,
                    'platform': rel.platform,
                    'download_url': rel.downloadURL,
                    'classifiers': rel.classifiers,
                    'requires': rel.requires,
                    # TODO: implement this
                    'requires_dist': [],
                    'provides': rel.provides,
                    # TODO: implement this
                    'provides_dist': [],
                    # TODO: implement this
                    'requires_external': [],
                    # TODO: implement this
                    'requires_python': '',
                    'obsoletes': rel.obsoletes,
                    # TODO: implement this
                    'obsoletes_dist': [],
                    # TODO: implement this
                    'project_url': []}
        return {}

    # TODO: implement this methods as described at:
    # http://wiki.python.org/moin/PyPiXmlRpc?action=show&redirect=CheeseShopXmlRpc
    def search(self, spec, operator='and'):
        raise NotImplementedError("search is not supported")

    def updated_releases(self, since):
        raise NotImplementedError("updated_releases is not supported")

    def changelog(self, since):
        raise NotImplementedError("search is not supported")
