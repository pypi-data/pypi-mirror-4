from z3c.form import error
from quintagroup.z3cform.captcha import widget

CaptchaFailureMessage = error.ErrorViewMessage(
    u'Please re-enter validation code.',
    error=ValueError,
    widget=widget.CaptchaWidget)
