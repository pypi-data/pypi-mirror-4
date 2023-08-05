### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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



from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ztfy.skin')


from fanstatic import Library, Resource
from ztfy.jqueryui import jquery, jquery_alerts, jquery_jsonrpc, jquery_tools


library = Library('ztfy.skin', 'resources')

ztfy_skin_css = Resource(library, 'css/ztfy.skin.css', minified='css/ztfy.skin.min.css')

ztfy_skin = Resource(library, 'js/ztfy.skin.js', minified='js/ztfy.skin.min.js',
                     depends=[ztfy_skin_css, jquery, jquery_alerts, jquery_jsonrpc, jquery_tools])
