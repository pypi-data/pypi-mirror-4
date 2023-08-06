Introduction
============

quintagroup.z3cform.captcha is a package that allows to add captcha to the z3c.form.
As a result such forms are prevented from automatic submit.

Captchas in a z3c form
----------------------

Using quintagroup.z3cform.captcha in a z3c.form form is simple.
Just add a Captcha field to your schema, use CaptchaWidgetFactory
widget factory for this field and away you go:

  >>> from zope.interface import Interface
  >>> from z3c.form import form, field
  >>> from quintagroup.z3cform.captcha import Captcha
  >>> from quintagroup.z3cform.captcha import CaptchaWidgetFactory

Now define form schema with Captch field 

  >>> class ICaptchaSchema(Interface):
  ...     captcha = Captcha(
  ...         title=_(u'Type the code'),
  ...         description=_(u'Type the code from the picture shown below.'))

And set proper widget factory for the captcha field

  >>>  class CaptchaForm(form.Form):
  ...      fields = field.Fields(ICaptchaSchema)
  ...      fields['captcha'].widgetFactory = CaptchaWidgetFactory


and z3c.form will take care of the rest. The widget associated with this field 
will render the captcha and verify the use input automatically.

Supported Plone versions
------------------------

quintagroup.z3cform.captcha was tested with Plone 3.0.6, 3.1.7, 3.2.3, 3.3.4.

Authors
-------

* Taras Melnychuk
* Andriy Mylenkyi
* Vitaliy Stepanov

Copyright (c) "Quintagroup": http://quintagroup.com, 2004-2010
