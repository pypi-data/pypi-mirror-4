from tw2.core import Param
from recaptcha.client.captcha import displayhtml, API_SERVER, API_SSL_SERVER
from tw2.forms import InputField

from tw2.core import templating, widgets

class ReCaptchaWidget(InputField):
    inline_engine_name = 'mako'

    template = """<div><script type="text/javascript" src="${w.server}/challenge?k=${w.public_key}${w.error_param}"></script>
<noscript>
  <iframe src="${w.server}/noscript?k=${w.public_key}${w.error_param}" height="300" width="500" frameborder="0"></iframe><br />
  <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript></div>
""" 

    type='text'
    public_key = Param(default=None, attribute=True)
    use_ssl = Param(default=False, attribute=True)
    error_param = Param(default=None, attribute=True)
    server = Param(default=API_SERVER, attribute=True)

    def prepare(self):
        """This method is called every time the widget is displayed. It's task
        is to prepare all variables that are sent to the template. Those
        variables can accessed as attributes of d."""

        if self.error_param:
            self.error_param = '&error=%s'%error_param

        if self.use_ssl:
            self.server = API_SSL_SERVER

        self.captcha_response = displayhtml(self.public_key)
        return super(ReCaptchaWidget, self).prepare()

