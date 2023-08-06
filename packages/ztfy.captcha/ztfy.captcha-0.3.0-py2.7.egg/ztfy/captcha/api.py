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
import logging
import os
import random
import string
import sys
from PIL import Image, ImageFont, ImageDraw, ImageFilter

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.utils import request as request_utils, session


SHA_FEED = str(random.randint(0, sys.maxint))

FONTS = {}
FONTS_PATH = os.path.join(os.path.dirname(__file__), 'fonts')
for f in os.listdir(FONTS_PATH):
    try:
        FONTS[f] = ImageFont.truetype(os.path.join(FONTS_PATH, f), random.randint(30, 40))
    except:
        logging.getLogger('ztfy.captcha').error("Can't load font from file '%s'" % f)


def getCaptchaImage(text, format='JPEG'):
    """Generate new captcha"""
    img = Image.new('RGB', (30 * len(text), 100), 0xffffff)
    img.format = format
    d = ImageDraw.Draw(img)
    x = y = 2
    height = random.randint(0, 35)
    for c in text:
        font = FONTS[random.choice(FONTS.keys())]
        w, h = font.getsize(c)
        height = max(height, h)
        y = random.randint(2, max(height - h, 2) + 10)
        d.text((x, y + 5), c, font=font, fill=0x333333)
        x += w
    height += 5
    for _i in range(5):
        d.line((random.randint(0, x / 2),
                random.randint(0, height),
                random.randint(x / 2, x),
                random.randint(0, height)), width=1, fill=0x888888)
    return img.crop((0, 0, x + 4, height + 4)).filter(ImageFilter.SMOOTH_MORE)


CHARS = string.ascii_uppercase + string.digits[1:]


def getDigest(text):
    return hashlib.sha256(SHA_FEED + '-----' + (text or '')).hexdigest()


def getCaptcha(id, length=5, format='JPEG', request=None):
    """Create a new random captcha"""
    text = ''.join([random.choice(CHARS) for _i in range(length)])
    image = getCaptchaImage(text, format)
    if request is None:
        try:
            request = request_utils.getRequest()
        except RuntimeError:
            pass
    if request is not None:
        session.setData(request, 'ztfy.captcha', id, getDigest(text))
    return text, image


def checkCaptcha(id, text, request=None):
    if request is None:
        try:
            request = request_utils.getRequest()
        except RuntimeError:
            return False
    digest = session.getData(request, 'ztfy.captcha', id)
    return getDigest(text) == digest
