from django.test import TestCase

from django.test.utils import setup_test_template_loader
from django.template.loader import get_template
from django.template import Context

TEMPLATES = {
    'form.html': '''
{% load formulation %}
{% form "formulation/default.form" %}
{% for field in form %}
{% field field "field" %}
{% endfor %}
{% endform %}
''',
}

class TestForm(forms.Form):
    first = forms.CharField()

class TagTest(TestCase):

    def setUp(self):
        setup_test_template_loader(TEMPLATES)

    def test_basic_test(self):
        context = Context({
            'form': TestForm(),
        })
        tmpl = get_template('form.html')
        output = tmpl.render(context)
        self.assertEqual('', output)
