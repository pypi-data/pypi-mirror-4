from formencode.validators import FancyValidator
from formencode import Invalid
import urllib, urllib2

import gettext
_ = gettext.gettext

class ReCaptchaValidator(FancyValidator):
    """
    @see formencode.validators.FieldsMatch
    """

    messages = {
        'incorrect': _("Incorrect value."),
        'missing':  _("Missing value."),
    }

    verify_server           = "api-verify.recaptcha.net"
    __unpackargs__ = ('*', 'field_names')

    validate_partial_form   = True
    validate_partial_python = None
    validate_partial_other = None

    def __init__(self, private_key, remote_ip, *args, **kw):
        super(ReCaptchaValidator, self).__init__(args, kw)
        self.private_key = private_key
        self.remote_ip = remote_ip
        self.field_names = ['recaptcha_challenge_field',
                            'recaptcha_response_field']
    
    def validate_partial(self, field_dict, state):
        for name in self.field_names:
            if not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        challenge = field_dict['recaptcha_challenge_field']
        response = field_dict['recaptcha_response_field']
        if response == '' or challenge == '':
            error = Invalid(self.message('missing', state), field_dict, state)
            error.error_dict = {'recaptcha_response_field':'Missing value'}
            raise error
        params = urllib.urlencode({
            'privatekey': self.private_key,
            'remoteip' : self.remote_ip,
            'challenge': challenge,
            'response' : response,
            })
        request = urllib2.Request(
            url = "http://%s/verify" % self.verify_server,
            data = params,
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "User-agent": "reCAPTCHA Python"
                      }
            )
        
        httpresp = urllib2.urlopen(request)
        return_values = httpresp.read().splitlines();
        httpresp.close();
        return_code = return_values[0]
        if not return_code == "true":
            error = Invalid(self.message('incorrect', state), field_dict, state)
            error.error_dict = {'recaptcha_response_field':self.message('incorrect', state)}
            raise error
        return True
