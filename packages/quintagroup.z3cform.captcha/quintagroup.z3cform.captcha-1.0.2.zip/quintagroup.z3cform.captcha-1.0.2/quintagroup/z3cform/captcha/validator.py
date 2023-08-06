from DateTime import DateTime

from zope.interface import Interface
from zope.component import adapts
from zope.i18n import MessageFactory

from Products.CMFCore.utils import getToolByName

from quintagroup.captcha.core.utils import decrypt, parseKey, encrypt1, getWord

from z3c.form.validator import SimpleFieldValidator

from quintagroup.z3cform.captcha.interfaces import ICaptcha

_ = MessageFactory('quintagroup.z3cform.captcha')


class CaptchaValidator(SimpleFieldValidator):
    """Captcha validator"""

    adapts(Interface, Interface, Interface, ICaptcha, Interface)

    def validate(self, value):
        # Verify the user input against the captcha
        if 'kss_z3cform_inline_validation' in self.request['URL']:
            return
        context = self.context
        request = self.request
        value = value or ''
        captcha_type = context.getCaptchaType()
        if captcha_type in ['static', 'dynamic']:
            hashkey = request.get('%shashkey' % self.widget.form.prefix, '')
            decrypted_key = decrypt(context.captcha_key, hashkey)
            parsed_key = parseKey(decrypted_key)

            index = parsed_key['key']
            date = parsed_key['date']

            if captcha_type == 'static':
                img = getattr(context, '%s.jpg' % index)
                solution = img.title
                enc = encrypt1(value)
            else:
                enc = value
                solution = getWord(int(index))

            captcha_tool = getToolByName(context, 'portal_captchas')
            if (enc != solution) or (captcha_tool.has_key(decrypted_key)) or \
               (DateTime().timeTime() - float(date) > 3600):
                raise ValueError(_(u'Please re-enter validation code.'))
            else:
                captcha_tool.addExpiredKey(decrypted_key)
