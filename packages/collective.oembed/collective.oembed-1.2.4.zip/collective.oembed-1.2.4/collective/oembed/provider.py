import json
from urlparse import urlparse
from collective.oembed.consumer import ConsumerAggregatedView
try:
    from zope.component.hooks import getSite
except ImportError:
    #BBB
    from zope.site.hooks import getSite

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
import logging
logger = logging.getLogger('collective.oembed')


class OEmbedProvider(BrowserView):
    """OEmbed Provider"""

    index_xml = ViewPageTemplateFile('provider_xml.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.format = None
        self.url = None
        self.maxwidth = None
        self.maxheight = None
        self.embed = {}

        self._site = None
        self._target = None

    def __call__(self):
        try:
            self.update()
            return self.render()
        except KeyError, e:
            return e
        except ValueError, e:
            return e

    def update(self):
#        import pdb;pdb.set_trace()
        if self.format is None:
            self.format = self.request.get('format', None)

        if self.format is None or not self.format:
            self.format = 'json'
        if self.format == 'json':
            self.request.response.setHeader('Content-Type', 'application/json')

        if self.format not in ('json', 'xml'):
            raise ValueError('format parameter must be in json, xml')

        if self.url is None:
            self.url = self.request.get('url', None)
        if self.url is None:
            raise KeyError('you must provide url parameter')

        if self.maxwidth is None:
            self.maxwidth = self.request.get('maxwidth', None)
        if self.maxheight is None:
            self.maxheight = self.request.get('maxheight', None)

        if not self.url.startswith(self.context.absolute_url()):
            return

        path = self.get_path()
        site = self.get_site()
        if site is None or path is None:
            return

        ob = self.get_target()
        if ob is None:
            return

        self.build_info(ob, site)

    def build_info(self, context, site):
        ob = context
        site_title = site.Title()

        title = ob.Title()
        if type(title) != unicode:
            title.decode('utf-8')
        if type(site_title) != unicode:
            site_title = site_title.decode('utf-8')

        e = self.embed
        e[u'version'] = '1.0'
        e[u'title'] = title
        e[u'author_name'] = ob.Creator()
        e[u'author_url'] = site.absolute_url() + '/author/' + ob.Creator()
        e[u'provider_name'] = site_title
        e[u'provider_url'] = site.absolute_url()
        field = ob.getPrimaryField()
        if field and field.type == 'text':
            e[u'type'] = 'rich'
            e[u'html'] = field.getAccessor(ob)()
        elif field and field.type == 'image':
            e[u'type'] = 'photo'
            e[u'url'] = ob.absolute_url()
            image = field.getAccessor(ob)()
            e[u'width'] = image.width
            e[u'height'] = image.height
        else:
            e[u'type'] = 'link'

    def render(self):
        res = self.embed
        if self.format == 'json':
            return json.dumps(res)

        return self.index_xml()

    def get_path(self):
        parsed = urlparse(self.url)
        path = parsed.path
        return path

    def get_site(self):
        if self._site is None:
            self._site = getSite()
        return self._site

    def get_target(self):
        site = self.get_site()
        path = self.get_path()
        portal_path = site.portal_url.getPortalPath()
        if path.startswith(portal_path):
            path = path[len(portal_path):]

        if site is None:
            return

        if self._target is None:
            try:
                # remove heading /
                self._target = site.restrictedTraverse(path[1:])
            except KeyError, e:
                logger.error('get_target error -> %s' % e)
                return

        return self._target


class ProxyOembedProvider(OEmbedProvider, ConsumerAggregatedView):
    """This oembed provider can be used as proxy consumer"""
    def __init__(self, context, request):
        OEmbedProvider.__init__(self, context, request)
        ConsumerAggregatedView.__init__(self, context, request)
        self.is_local = False

    def update(self):
        if self.url is None:
            self.url = self.request.get('url', None)

        OEmbedProvider.update(self)  # update in all case
        if self.url.startswith(self.context.absolute_url()):
            self.is_local = True
        else:
            ConsumerAggregatedView.update(self)
            self._url = self.url
            self._maxheight = self.maxheight
            self._maxwidth = self.maxwidth

    def __call__(self):
        self.update()
        if self.is_local:
            result = OEmbedProvider.__call__(self)
        else:

            result = ConsumerAggregatedView.get_data(self,
                                    self.url,
                                    maxwidth=self.maxwidth,
                                    maxheight=self.maxheight,
                                    format="json")

            if type(result) == dict:
                result = json.dumps(result)

        return result
