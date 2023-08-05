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

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from z3c.form import field
from zope.component import adapts
from zope.interface import Interface, implements

# import local packages
from ztfy.captcha.schema import Captcha
from ztfy.skin.form import EditSubForm

from ztfy.captcha import _


class ICaptchaInfo(Interface):
    """Captcha infos interface"""

    captcha = Captcha(title=_("Verification code"),
                      description=_("This code is used to protect this form against automatic spams.\n"
                                    "Code is made of 6 characters (letters and numbers from 1 to 9)."),
                      required=True)


class CaptchaAdapter(object):

    adapts(Interface)
    implements(ICaptchaInfo)

    def __init__(self, context):
        self.context = context

    def _getCaptcha(self):
        return None

    def _setCaptcha(self, value):
        pass

    captcha = property(_getCaptcha, _setCaptcha)


class CaptchaSubForm(EditSubForm):
    """Generic captcha sub-form"""

    prefix = 'captcha.'
    tabLabel = _("Anti-spam code")

    fields = field.Fields(ICaptchaInfo)
    ignoreContext = True
