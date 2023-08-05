# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.utils.log import getLogger
logger = getLogger('django.request')

_HTML_DOCTYPE = _HTML_RENDER_METHOD = _HTML_ENCODING = ''
try:
    from asv_media.settings import Settings
    settings = Settings()
    _HTML_DOCTYPE = settings.ASV_MEDIA__HTML_DOCTYPES[settings.ASV_MEDIA__HTML_DOCTYPE]
    _HTML_RENDER_METHOD = settings.ASV_MEDIA__HTML_RENDER_METHOD
    _HTML_ENCODING = settings.ASV_MEDIA__HTML_ENCODING
except:
    _HTML_DOCTYPE = _HTML_DOCTYPE or '<!DOCTYPE HTML>'
    _HTML_RENDER_METHOD = _HTML_RENDER_METHOD or 'html'
    _HTML_ENCODING = _HTML_ENCODING or 'utf-8'
#

try:
    import lxml.html
    import lxml.etree
except ImportError:
    logger.warning('Forbidden (lxml midule not installed): %s' % request.path,
        extra={
            'status_code': 404,
        }
    )


CRLF2UNIX = re.compile('\r\n|\n\r?',re.M)

class HTML2eltreeMiddleware(object):
    def process_response(self, request, response):
        mmm = {}
        response.lxml_etree = None
        he = response._headers.get('content-type')
        if not he or response.status_code != 200 :
            return response
        c = he[1].split(';')[0]
        if c in ('text/html', 'application/xhtml+xml', 'application/xml'):
            doc = '{0}'.format(response.content.decode('utf-8'))
            doc = CRLF2UNIX.sub('\n',doc)
            doc = lxml.html.fromstring(doc)
            response.lxml_etree = doc
        else:
            pass
        return response
#
class Eltree2HTMLMiddleware(object):
    def process_response(self, Request, Response):
        def indent(elem, level=0):
            tt = '\n' + level * '  '
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = tt + '  '
                if not elem.tail or not elem.tail.strip():
                    elem.tail = tt
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = tt
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = tt
        #
        try:
            doc = Response.lxml_etree
        except Exception:
            doc = None
        if doc is None:
            #ErrResponse(Request,Response,'NO lxml_etree in reponse!')
            return Response
        indent(doc)
        Response.content = lxml.etree.tostring(doc.getroottree(),
            doctype = _HTML_DOCTYPE,
            method  = _HTML_RENDER_METHOD,
            encoding= _HTML_ENCODING,
            #pretty_print=False,
        )
        return Response
#


