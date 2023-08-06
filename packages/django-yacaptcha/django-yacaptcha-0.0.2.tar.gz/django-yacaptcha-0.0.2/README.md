=====
Django YaCaptcha
=====

Django YaCaptcha - Yandex Captcha (cleanweb) form field/widget integration app.

Uses https://github.com/coagulant/cleanweb

Quick start
-----------

1. Add "yacaptcha" to your INSTALLED_APPS setting like this:
<pre>
INSTALLED_APPS = (
        'yacaptcha',
)
</pre>

2. Get the API key http://api.yandex.ru/cleanweb and add to your project settings:
<pre>
YACAPTCHA_KEY = 'your_api_key'
</pre>

3. Add YaCaptchaField in your form like this::
<pre>
from yacaptcha.fields import YaCaptchaField
class TestForm(forms.Form):
        name = forms.CharField()
        captcha = YaCaptchaField()
</pre>
4. Add form field widget template
    You may create your own template for field widget. For this add in project settings:
<pre>
YACAPTCHA_WIDGET_TEMPLATE = 'path_to_widget.html'
</pre>
    Or use default widget.html from package django-yacaptcha/templates/yacaptcha/widget.html

5. If you use django-registration, you may use registartion backend with yacaptcha field like this:
<pre>
url(r'^accounts/', include('yacaptcha.backends.default.urls')), # yacaptcha backend for registration form
(r'^accounts/', include('registration.backends.default.urls')),
</pre>
