### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages
from cStringIO import StringIO

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.captcha.api import getCaptcha


class CaptchaView(object):
    """Generate and returns a captcha image"""

    def getCaptcha(self):
        _text, img = getCaptcha(id=self.request.form.get('id'), length=6, request=self.request)
        data = StringIO()
        img.save(data, 'JPEG')
        img_data = data.getvalue()
        if self.request is not None:
            self.request.response.setHeader('Content-Type', 'image/jpeg')
            self.request.response.setHeader('Content-Length', len(img_data))
            self.request.response.setHeader('Cache-Control', 'private,no-cache,no-store')
        return img_data
