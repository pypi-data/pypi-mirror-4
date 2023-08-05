# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings as dj_settings

ASV_MEDIA__STATIC_ROOT = dj_settings.STATIC_URL.rstrip('/')
#---------------------------------------------------------------
#---------------------------------------------------------------
ASV_MEDIA__HTML_RENDER_METHOD = 'html'
ASV_MEDIA__HTML_DOCTYPE  = 'html5'
ASV_MEDIA__HTML_ENCODING = 'utf-8'
ASV_MEDIA__HTML_DOCTYPES = {
    'html5': '<!DOCTYPE HTML>',
    'html4': '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
    'xhtml': '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
}
ASV_MEDIA__HTML_DOCTYPES['html'] = ASV_MEDIA__HTML_DOCTYPES['html5']
ASV_MEDIA__HTML_DOCTYPES['xml']  = ASV_MEDIA__HTML_DOCTYPES['xhtml']
#---------------------------------------------------------------
#---------------------------------------------------------------
ASV_MEDIA__JQUERY_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js'
ASV_MEDIA__JQUERY_LOCATION_LOCAL = '{0}/lib/jquery-1.8.2.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERYUI_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js'
ASV_MEDIA__JQUERYUI_LOCATION_LOCAL = '{0}/lib/jquery-ui/jquery-ui-1.8.18.custom.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERYUI_CSS_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/themes/redmond/jquery-ui.css'
ASV_MEDIA__JQUERYUI_CSS_LOCATION_LOCAL = '{0}/lib/jquery-ui/css/smoothness/jquery-ui-1.8.18.custom.css'.format(ASV_MEDIA__STATIC_ROOT)

ASV_MEDIA__JQUERY_COOKIE_LOCATION = '{0}/lib/jquery.cookie.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERY_JSON_LOCATION = '{0}/lib/jquery.json.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERY_PJAX_LOCATION = '{0}/lib/jquery.pjax.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERY_COLORBOX_LOCATION = '{0}/lib/colorbox/jquery.colorbox-min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JQUERY_COLORBOX_CSS_LOCATION = '{0}/lib/colorbox/colorbox.css'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__PLUPLOAD_ROOT = '{0}/lib/plupload'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__BACKBONE = '{0}/lib/backbone-min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__UNDERSCORE = '{0}/lib/underscore-min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JSON = '{0}/lib/json.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__JSON2 = '{0}/lib/json2.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__KNOCKOUT = '{0}/lib/knockout-2.2.0.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__KNOCKBACK_FULL_STACK = '{0}/lib/knockback-full-stack.min.js'.format(ASV_MEDIA__STATIC_ROOT)
ASV_MEDIA__KNOCKBACK = '{0}/lib/knockback.min.js'.format(ASV_MEDIA__STATIC_ROOT)
#---------------------------------------------------------------
#---------------------------------------------------------------
ASV_MEDIA__DEFAULT_MEDIAFILES = {
        'text/css': (
            ASV_MEDIA__JQUERYUI_CSS_LOCATION,
        ),
        'text/javascript': (
            ASV_MEDIA__JQUERY_LOCATION,
            ASV_MEDIA__JQUERYUI_LOCATION,
            ASV_MEDIA__JQUERY_COOKIE_LOCATION,
            ASV_MEDIA__JQUERY_JSON_LOCATION,
        ),
}
#---------------------------------------------------------------
#---------------------------------------------------------------
