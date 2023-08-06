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
import hashlib

# import Zope3 interfaces
from z3c.form.interfaces import IFieldWidget, ITextWidget, IValidator, IErrorViewSnippet
from zope.schema.interfaces import IField

# import local interfaces
from ztfy.captcha.schema import ICaptcha
from ztfy.skin.layer import IZTFYBrowserLayer

# import Zope3 packages
from z3c.form.browser.text import TextWidget
from z3c.form.error import ErrorViewSnippet
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts
from zope.interface import Interface, implementer, implements, implementsOnly
from zope.schema import ValidationError

# import local packages
from ztfy.captcha.api import checkCaptcha
from ztfy.utils.catalog import getObjectId

from ztfy.captcha import _


class ICaptchaWidget(ITextWidget):
    """Captcha widget interface"""


class CaptchaWidget(TextWidget):
    """Captcha widget"""

    implementsOnly(ICaptchaWidget)

    ignoreContext = True
    ignoreRequest = True
    klass = u'captcha-widget'

    @property
    def captcha_id(self):
        token = '%d::%s' % (getObjectId(self.context), self.name)
        return hashlib.sha256(token).hexdigest()


@adapter(IField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def CaptchaFieldWidget(field, request):
    """ICaptchaWidget factory"""
    return FieldWidget(field, CaptchaWidget(request))


class CaptchaValidator(SimpleFieldValidator):
    """Captcha field validator"""

    adapts(Interface, IZTFYBrowserLayer, Interface, ICaptcha, ICaptchaWidget)
    implements(IValidator)

    def validate(self, value):
        result = super(CaptchaValidator, self).validate(value)
        if value:
            id = self.widget.captcha_id
            if not checkCaptcha(id, value.upper(), self.request):
                raise ValidationError, "Invalid captcha"
        return result


class CaptchaErrorSnippet(ErrorViewSnippet):
    """Captcha error view snippet"""

    adapts(ValidationError, None, ICaptchaWidget, None, None, None)
    implements(IErrorViewSnippet)

    def createMessage(self):
        return _("Invalid captcha input")
