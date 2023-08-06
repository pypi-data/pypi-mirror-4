import subprocess
import tempfile
import os
import shutil
import re
import StringIO

from copy import deepcopy
from urllib2 import urlopen

from BeautifulSoup import BeautifulSoup, Tag

from AccessControl import Unauthorized

from zope import interface
from zope import component
from zope.browser.interfaces import IBrowserView

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.FSDTMLMethod import FSDTMLMethod

from raptus.princexml import interfaces

prince = os.environ.get('PRINCE_EXECUTABLE', 'prince')
css_import_re = re.compile('@import [url]{3}?\(?\s*\"([^\"]+)\"\s*\)?[^;]*;')
css_resource_re = re.compile('url\(\s*\"?([^\"^\s]+)\"?\s*\)')


class PDFConverter(object):
    """ Adapter to convert a view to a PDF using PrinceXML
    """
    interface.implements(interfaces.IPDFConverter)
    component.adapts(IBrowserView)

    def __init__(self, view):
        self._dir = None
        self.view = view
        self._resourceid = 1
        self._headers = deepcopy(view.request.response.headers)
        self.portal_state = component.getMultiAdapter((view.context, view.request), name=u'plone_portal_state')
        self.portal = self.portal_state.portal()
        self.mtypes = getToolByName(self.portal, 'mimetypes_registry')
        self.portal_url = self.portal_state.portal_url()

    def __call__(self, method='__call__', destination=None):
        """ Returns the contents of the PDF as a stream or
            writes them directly into the provided destination
        """
        try:
            filename = self._download(method)
            ret = destination is None
            if ret:
                destination = os.path.join(os.path.dirname(filename), 'index.pdf')
            subprocess.call([prince, "--input=html", filename, "-o", destination])
            if not os.path.isfile(destination):
                result = False
            else:
                result = True
                if ret:
                    result = StringIO.StringIO()
                    file = open(destination, 'r')
                    for line in file:
                        result.write(line)
                    file.close()
        finally:
            self._cleanup()
        return result

    def _download(self, method):
        if not hasattr(self.view, method):
            raise ValueError('method', 'The given method is not available for the view')
        self._dir = tempfile.mkdtemp()
        html = BeautifulSoup(getattr(self.view, method)())

        # Convert CSS imports and links to inline
        css = u''
        for link in html.findAll(['style', 'link']):
            if link.name == 'style':
                css += link.contents + u'\n\n'
            elif link['rel'] == 'stylesheet':
                css += self._get_css(link['href']) + u'\n\n'
            link.extract()

        # Convert @import statements
        while True:
            match = css_import_re.search(css)
            if not match:
                break
            start, end = match.span()
            css = css[:start] + u'\n\n' + self._get_css(match.group(2)) + u'\n\n' + css[end:]

        # Download resources referenced in CSS and adjust the URLs
        converted = u''
        while True:
            match = css_resource_re.search(css)
            if not match:
                break
            start, end = match.span()
            converted += css[:start] + u'url("' + self._download_resource(match.group(1)) + u'")'
            css = css[end:]
        css = converted + css

        file = open(os.path.join(self._dir, 'style.css'), 'w')
        file.write(css)
        file.close()
        style = Tag(html, 'link', {'rel': u'stylesheet', 'media': u'all', 'href': 'style.css'})
        html.find('head').insert(0, style)

        # Download all images and adjust the src attributes
        for img in html.findAll('img'):
            img['src'] = self._download_resource(img['src'])

        file = open(os.path.join(self._dir, 'index.html'), 'w')
        file.write(html.renderContents())
        file.close()
        return file.name

    def _download_file(self, url, force_download=False):
        if not force_download and not '?' in url and url.startswith(self.portal_url):
            try:
                file = self.portal.restrictedTraverse(str(url[len(self.portal_url) + 1:]))
                if isinstance(file, FSDTMLMethod):
                    file = file(self.portal)
                if hasattr(file, '_readFile'):
                    file = file._readFile(False)
                if hasattr(file, 'GET'):
                    file = file.GET()
                return file
            except:
                pass
        return urlopen(url).read()

    def _get_css(self, url):
        file = self._download_file(url)
        if not isinstance(file, basestring):
            try:
                file = file()
            except:
                file = self._download_file(url, True)
        if isinstance(file, basestring):
            return file
        return u''

    def _download_resource(self, url):
        hash = None
        ext = None
        resource = None
        if '#' in url:
            url, hash = url.split('#')
        if u'at_download' in url:
            url = url.replace(u'/at_download', '')
        else:
            resource = self._download_file(url)
            if not isinstance(resource, basestring):
                resource = self._download_file(url, True)
        if not isinstance(resource, basestring) and url.startswith(self.portal_url):
            parts = url.split('/')
            field = parts.pop()
            scale = None
            try:
                context = self.portal.restrictedTraverse(str('/'.join(parts)[len(self.portal_url) + 1:]))
            except Unauthorized:
                return u''
            if field.startswith('image_'):
                field, scale = field.split('_')
            image = context.Schema()[field].get(context)
            if image is not None:
                filename = image.getFilename()
                if filename is None:
                    mime = self.mtypes.lookup(image.getContentType())
                    if len(mime) and len(mime[0].extensions):
                        ext = mime[0].extensions[0]
                else:
                    parts = filename.split('.')
                    if len(parts):
                        ext = parts[-1]
                resource = image.data
        if not isinstance(resource, basestring):
            if hash is not None:
                url += u'#' + hash
            return url
        if ext is None:
            parts = url.split('.')
            if len(parts):
                ext = parts[-1]
        filename = 'resource%s.%s' % (self._resourceid, ext)
        file = open(os.path.join(self._dir, filename), 'w')
        file.write(resource)
        file.close()
        self._resourceid += 1
        if hash is not None:
            filename += u'#' + hash
        return filename

    def _cleanup(self):
        if self._dir is not None and os.path.isdir(self._dir):
            shutil.rmtree(self._dir)
        self.view.request.response.headers = self._headers
