# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
from asv_utils.common import *
from django.conf import settings
from django.core.exceptions import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.functional import lazy
from django.core.urlresolvers import reverse, resolve
from django.core.files.storage import FileSystemStorage
#FSS = FileSystemStorage(location=settings.MEDIA_ROOT)
#---------------------------------------------------------------
#---------------------------------------------------------------
def Return404(request,addParams={},U='',tmpl='admin/404.html',**kwargs):
    P = {
         'URI': request.get_full_path(),
         'BODYCLASS': 'all',
    }
    if addParams:
      P.update(addParams)
    R = render_to_response(tmpl,P,context_instance=RequestContext(request))
    return R
#---------------------------------------------------------------
#---------------------------------------------------------------
def Return50x(request,addParams={},U='',tmpl='admin/404.html',**kwargs):
    P = {
         'URI': request.get_full_path(),
         'BODYCLASS': 'all',
    }
    if addParams:
      P.update(addParams)
    R = render_to_response(tmpl,P,context_instance=RequestContext(request))
    return R
#---------------------------------------------------------------
#---------------------------------------------------------------
#try:
#    from django.core.urlresolvers import reverse_lazy
#except ImportError:
reverse_lazy = lambda *args, **kwargs : lazy(reverse, str)(*args, **kwargs)
#---------------------------------------------------------------
#---------------------------------------------------------------
def may_be_json(f, *args, **kwargs):
    @wraps(f)
    def ex(req, *args, **kwargs):
        rv = f(req, *args, **kwargs)
        if type(rv) in (type(''), type(()), type([]), type({})):
            rv = json.dumps(rv, indent=4) if rv else '{}'
            resp = HttpResponse(mimetype='application/json')
            resp.write(rv)
            rv = resp
        return rv
    return ex
#---------------------------------------------------------------
#---------------------------------------------------------------

