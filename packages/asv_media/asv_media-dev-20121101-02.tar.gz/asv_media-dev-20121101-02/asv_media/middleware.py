# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.conf import settings as dj_settings
from lxml.builder import E
from asv_media.settings import settings as AMS
from django.utils.log import getLogger
logger = getLogger('django.request')
ADMIN_MEDIA_PREFIX = '{0}admin/'.format(dj_settings.STATIC_URL)
#-------------------------------------------------------
#-------------------------------------------------------
MediaProcessing = {
    'text/css': (
        { 'LIB': 'JQUERYUI',
            'R': (
                re.compile(r'\/([\.\d]+)+\/themes\/\w+\/jquery-ui.css$',re.I),
            )
        },
#        { 'LIB': 'COLORBOX',
#            'R': (
#                re.compile(r'\/colorbox.css$',re.I),
#            )
#        },
    ),
    'text/javascript': (  # PASS sections need be first
        { 'LIB':'DJJQUERY',
          'R':(
              re.compile(
                re.sub(r'/+','/',r'{0}/js/jquery(\.min)*\.js$'.format(ADMIN_MEDIA_PREFIX))
              ),
          ),
          'PASS':True,
        },
        { 'LIB':'JQUERY',
          'R':(
              re.compile(r'jquery(\.min)*\.js$',re.I),
              re.compile(r'\/([\.\d]+)*\/jquery(\.min)*\.js$',re.I),
              re.compile(r'jquery([-\.\d]+)*(\.min)*\.js$',re.I)
            ),
        },
        { 'LIB': 'JQUERYUI',
          'R':(
              re.compile(r'jquery-ui(\.min)*\.js$',re.I),
              re.compile(r'\/([\.\d]+)*\/jquery-ui(\.min)*\.js$',re.I),
              re.compile(r'jquery-ui([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
        { 'LIB':'JQUERYCOOKIE',
          'R':(
              re.compile(r'jquery[\.\_]+cookie([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
#        { 'LIB':'COLORBOX',
#          'R':(
#              re.compile(r'jquery[\.\_\-]+colorbox([-\.\d]+)*([\.\_\-]min)*\.js$',re.I),
#          ),
#        },
        { 'LIB': 'JQUERYJSON',
          'R':(
              re.compile(r'jquery[\.\_]+json([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
    )
}
#-------------------------------------------------------
#-------------------------------------------------------
class AddSomeJS(object):
    MediaFiles = []
    def process_request(self, Request):
        # reverse do not work in process_response :(
        # We need use it here :(
        if not self.MediaFiles:
            for T in AMS.ASV_MEDIA__DEFAULT_MEDIAFILES:
                for i in AMS.ASV_MEDIA__DEFAULT_MEDIAFILES[T]:
                    EEE = None
                    if T == 'text/css':
                        EEE = E('link',
                            rel  = 'stylesheet',
                            type = 'text/css',
                            href = '{0}'.format(i),
                        )
                    elif T == 'text/javascript':
                        EEE = E('script',
                            type = 'text/javascript',
                            src = '{0}'.format(i),
                        )
                    else:
                        continue
                    if EEE is not None:
                        self.MediaFiles.append(EEE)
    def process_response(self, Request, Response):
        doc = Response.lxml_etree
        if doc is None:
            return Response
        try:
            hh = doc.xpath('head')[0]
        except IndexError:
            return Response
        pos = 0
        for i in self.MediaFiles:
            hh.insert(pos, i)
            pos += 1
        return Response
#-------------------------------------------------------
#-------------------------------------------------------
class FilterSomeJS(object):
    def process_response(self, Request, Response):
        def ErrResponse(Req, Resp, txt):
            if dj_settings.DEBUG:
                print('asv_media::{0}::{1}'.format(Req.path,txt))
        doc = Response.lxml_etree
        if doc is None:
            #ErrResponse(Request,Response,'NO lxml_etree in reponse!')
            return Response
        try:
            hh = doc.xpath('head')[0]
        except IndexError:
            return Response
        ## Collecting Styles and Scripts from HTML header
        ## and put LINKS (eltree objects) to it to LibsInHtmlHead dictionary
        MediaTypes=('text/css','text/javascript')
        LibsInHtmlHead = {}
        for TypeTag in MediaTypes:
            LibsInHtmlHead[TypeTag]=[]
        k=0
        for TypeTag in ('link','script'):
            ll = hh.xpath(TypeTag)
            for LIB in ll:
                t=LIB.attrib.get('type')
                if t and t==MediaTypes[k]:
                    uri=LIB.attrib.get('src',LIB.attrib.get('href'))
                    if uri:
                        LibsInHtmlHead[MediaTypes[k]].append((LIB,uri,))
            k+=1
        ## detecting multiple entering monitored JS and CSS
        ## and putting links to it to WillBeRemoved
        WillBeRemoved = {}
        for T in MediaTypes:
            q = WillBeRemoved.get(T)
            if not q:
                WillBeRemoved[T] = {}
            for H in LibsInHtmlHead[T]:
                for Rg in MediaProcessing[T]:
                    OK = False
                    q = WillBeRemoved[T].get(Rg['LIB'])
                    if not q:
                        WillBeRemoved[T][Rg['LIB']] = []
                    for R in Rg['R']:
                        if R.search(H[1]):
                            if Rg.get('PASS'):
                                pass
                            else:
                                WillBeRemoved[T][Rg['LIB']].append({
                                    'EL': H[0],
                                    'URI': H[1],
                                })
                            OK = True
                            break
                    if OK:
                        break
        ## Removing repeated JS and CSS
        for TypeTag in WillBeRemoved:
            if not WillBeRemoved[TypeTag]:
                continue
            for LIB in WillBeRemoved[TypeTag]:
                if not WillBeRemoved[TypeTag][LIB]:
                    continue
                kk = 0
                for k in WillBeRemoved[TypeTag][LIB]:
                    EE = k['EL']
                    EE.clear()
                    EE.getparent().remove(EE)
                    kk+=1
        return Response
#-------------------------------------------------------
#-------------------------------------------------------
class MovingUnbodiedJStoHead(object):
    def process_response(self, Request, Response):
        def DeleteForDeDupMedia(A):
            removeFromA = []
            a = 0
            for i in A:
                try:
                    removeFromA.index(a)
                    continue
                except Exception:
                    pass
                s = a + 1
                if s > len(A)-1:
                    continue
                b = s
                for j in A[s:]:
                    if i[1] == j[1]:
                        removeFromA.append(b)
                    b+=1
                a+=1
            return removeFromA

        def ErrResponse(Req, Resp, txt):
            if dj_settings.DEBUG:
                print('asv_media::{0}::{1}'.format(Req.path,txt))
        doc = Response.lxml_etree
        if doc is None:
            #ErrResponse(Request,Response,'NO lxml_etree in reponse!')
            return Response
        ## Collecting Styles and Scripts from HTML
        ## and put LINKS (eltree objects) to it to MediaLibs dictionary
        MediaLibs = {}
        MediaTypes= ('text/css','text/javascript')
        MediaTags = ('link','script')
        HtmlParts = ('head','body')
        MoveToHead = []
        k=0
        for T in MediaTypes:
            MediaLibs[T] = []
            h = 0
            for P in HtmlParts:
                try:
                    HB = doc.xpath(P)[0]
                except Exception, e:
                    continue
                ll = HB.getiterator(tag=MediaTags[k])
                for LIB in ll:
                    t=LIB.attrib.get('type')
                    if t and t==T:
                        uri=LIB.attrib.get('src',LIB.attrib.get('href'))
                        if uri:
                            MediaLibs[T].append((LIB,uri))
                            if h>0:
                                MoveToHead.append((LIB,uri))
                h+=1
            k+=1
            BeDel = DeleteForDeDupMedia(MediaLibs[T])
            ddd = []
            for i in BeDel:
                ddd.append(MoveToHead.index(MediaLibs[T][i]))
            ddd.sort()
            ddd.reverse()
            for i in ddd:
                del(MoveToHead[i])
            BeDel.sort()
            BeDel.reverse()
            for i in BeDel:
                EE = MediaLibs[T][i][0]
                EE.clear()
                EE.getparent().remove(EE)
                del(MediaLibs[T][i])
        try:
            hh = doc.xpath('head')[0]
            pos = len(hh)
            for i in MoveToHead:
                hh.insert(pos, i[0])
                # убивать не надо, insert выше работает как move
                #EE = i[0]
                #EE.clear()
                #EE.getparent().remove(EE)
                pos += 1
        except Exception, e:
            if dj_settings.DEBUG:
                print('error in deduplicating JS and CSS middleware:\n  {0}'.format(e))
        return Response
#-------------------------------------------------------
#-------------------------------------------------------
