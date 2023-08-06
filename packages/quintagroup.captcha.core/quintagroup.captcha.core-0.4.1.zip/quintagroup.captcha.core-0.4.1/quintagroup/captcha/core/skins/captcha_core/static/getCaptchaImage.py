## Script (Python) "getCaptchaImage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
from quintagroup.captcha.core.utils import gen_captcha, decrypt, \
    getWord, parseKey

try:
    hk = context.REQUEST.traverse_subpath[0]
except IndexError:
    return
try:
    dk = decrypt(context.captcha_key, hk)
except:
    return
key = parseKey(dk)['key']
try:
    img = getattr(context, '%s.jpg' % key)
except AttributeError:
    return
return img.index_html(context.REQUEST, context.REQUEST.RESPONSE)
