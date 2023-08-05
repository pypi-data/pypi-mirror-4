from zope.publisher.browser import BrowserView


class SimpleCaptchaView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def image_tag(self):
        return '<input name="test_captcha" type="hidden" />'

    def audio_url(self):
        return None

    def verify(self, input=None):
        return self.request.get('test_captcha', None) == 'please_ignore'

    @property
    def external(self):
        return True
