from zope.app.form.interfaces import WidgetInputError, InputErrors
from plone.app.users.browser import register

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CaptchaMixin(object):

    template = ViewPageTemplateFile('register_form.pt')

    # Assume the related field is called captcha.
    captcha_id = 'captcha'
    captcha_label = u'label_captcha'
    captcha_errmsg = ''

    def getCaptcha(self):
        result = self.context.restrictedTraverse('@@captcha', None)
        return result

    def hasCaptcha(self):
        return self.getCaptcha() is not None

    def image_tag(self):
        return self.getCaptcha().image_tag()

    def validate_captcha(self, action, data):
        errors = []

        captcha = self.getCaptcha()
        if captcha is None:
            # nothing to be done, and we won't fail prematurely here.
            return errors
 
        if not captcha.verify():
            errors.append(WidgetInputError(
                self.captcha_id, self.captcha_label, self.captcha_errmsg))

        return errors


class CaptchaRegistrationForm(CaptchaMixin, register.RegistrationForm):

    def validate_registration(self, action, data):
        errors = super(CaptchaRegistrationForm, self).validate_registration(
            action, data)
        errors.extend(self.validate_captcha(action, data))
        return errors
