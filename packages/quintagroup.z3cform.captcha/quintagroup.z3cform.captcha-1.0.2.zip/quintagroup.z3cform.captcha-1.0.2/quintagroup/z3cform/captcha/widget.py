from zope.interface import implementer

from z3c.form import interfaces
from z3c.form import widget

from Products.CMFCore.utils import getToolByName

from z3c.form.browser.text import TextWidget


class CaptchaError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CaptchaWidget(TextWidget):

    def getCaptcha(self):
        try:
            return self.form.context.getCaptcha()
        except AttributeError:
            raise CaptchaError('quintagroup.captcha.core not installed. '
                               'Install quintagroup.captcha.core using '
                               'Quickinstaller or Plone Control Panel')

    def render(self):
        key = self.getCaptcha()
        portal_url = getToolByName(self.form.context, 'portal_url')()
        image_url = "%s/getCaptchaImage/%s" % (portal_url, key)

        return u"""<input type="hidden" value="%s" name="%shashkey" />
                   %s
                   <img src="%s" alt="Enter the word"/>""" % (
            key,
            self.form.prefix,
            super(CaptchaWidget, self).render(),
            image_url)
        return super(CaptchaWidget, self).template(self)


@implementer(interfaces.IFieldWidget)
def CaptchaWidgetFactory(field, request):
    return widget.FieldWidget(field, CaptchaWidget(request))
