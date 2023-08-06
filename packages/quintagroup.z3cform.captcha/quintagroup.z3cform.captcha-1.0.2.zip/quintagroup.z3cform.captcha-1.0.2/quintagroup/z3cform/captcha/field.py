from zope.interface import implements
from zope.schema import ASCIILine
from quintagroup.z3cform.captcha.interfaces import ICaptcha


class Captcha(ASCIILine):
    implements(ICaptcha)
