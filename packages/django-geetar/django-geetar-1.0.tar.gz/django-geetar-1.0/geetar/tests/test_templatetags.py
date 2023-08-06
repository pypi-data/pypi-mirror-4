from django.utils import unittest
from django.utils.encoding import force_unicode

from base import TemplateTestCase

from geetar.templatetags.geetar import even, odd, split, possessive, jsonify, \
                                       paragraphlist, multibyte_truncate


class SimpleFiltersTestCase(TemplateTestCase):

    global_template_string = '{% load geetar %}'

    def test_odd_even(self):

        # Raw

        self.assertTrue(even(2))
        self.assertTrue(even(10))
        self.assertTrue(even(84))
        self.assertTrue(even(-48))
        self.assertFalse(even(3))
        self.assertFalse(even(69))
        self.assertFalse(even(1001))
        self.assertFalse(even(-175))

        self.assertTrue(odd(1))
        self.assertTrue(odd(11))
        self.assertTrue(odd(1001))
        self.assertTrue(odd(-13))
        self.assertFalse(odd(2))
        self.assertFalse(odd(10))
        self.assertFalse(odd(84))
        self.assertFalse(odd(-48))

        # Template

        self.assertTrue(self.render_template('{{ 2|even }}'))
        self.assertTrue(self.render_template('{{ "3"|odd }}'))
        self.assertEqual(self.render_template('{% if number|even %}Even number{% endif %}', {'number': 2}), 'Even number')

    def test_split(self):

        # Raw

        self.assertEqual(['Hello', 'there', 'sir'], split("Hello, there, sir"))
        self.assertEqual(['This', 'used', 'to', 'be', 'a', 'slug'], split("This-used-to-be-a-slug", '-'))

        # Template

        self.assertEqual(u'I-like-coffee-', self.render_template('{% with "I, like, coffee"|split as list %}{% for word in list %}{{ word }}-{% endfor %}{% endwith %}'))
        self.assertEqual(u'You, smell, funny, ', self.render_template('{% with "You-smell-funny"|split:"-" as list %}{% for word in list %}{{ word }}, {% endfor %}{% endwith %}'))

    def test_possessive(self):

        # Raw

        self.assertEqual("George's", possessive("George"))
        self.assertEqual("Chris'", possessive("Chris"))

        # Template

        self.assertEqual("Tom&#39;s", self.render_template('{{ "Tom"|possessive }}'))
        self.assertEqual("Sally&#39;s", self.render_template('{{ name|possessive }}', {'name': 'Sally'}))

    def test_jsonify(self):

        data = [
            {
                'id': 1,
                'name': 'Bill'
            },
            {
                'id': 2,
                'name': 'Sam'
            },
            {
                'id': 3,
                'name': 'Mr. Giggles'
            }
        ]

        data_string = u'[{"id": 1, "name": "Bill"}, {"id": 2, "name": "Sam"}, {"id": 3, "name": "Mr. Giggles"}]'

        self.assertEqual(data_string, self.render_template("{{ data|jsonify }}", {'data': data}))

    def test_paragraphlist(self):

        text = """Hello, here's the first paragraph.

        Oh, hey. Here's the 2nd paragraph."""

        # Raw

        self.assertEqual(["Hello, here's the first paragraph.", "Oh, hey. Here's the 2nd paragraph."], paragraphlist(text))

        # Template

        text = """
        Hey dude.

        What's up?
        """

        self.assertEqual(u"<p>Hey dude.</p><p>What&#39;s up?</p>", self.render_template('{% for para in text|paragraphlist %}<p>{{ para }}</p>{% endfor %}', {'text': text}))


    def test_multibyte_truncate(self):

        basic_text = '<h1>Oh hey there, fancypants</h1>'
        self.assertEqual("<h1>Oh ...</h1>", multibyte_truncate(basic_text, "1,1"))

        multibyte_text = u"<p>\u3046 \u305f\u3093 \u3041\u3093 \u3042\u3044\u3093 \u306e\u3072\u3093 \u3068 \u3075 \u3046\u3043<p>"
        self.assertEqual(u"<p>\u3046 ...</p>", multibyte_truncate(multibyte_text, "0,1"))


class ColumnizeTagTestCase(TemplateTestCase):
    
    """
    Tests for 'columnize' template tag
    """
    
    global_template_string = '{% load geetar %}'
    
    def test_basic(self):
        
        # Basic
        
        mylist = ['hello', 'there', 'dude']
        expr = '{% columnize mylist into 3 %}'
        rendered, context = self.render(expr, {'mylist': mylist})
        
        self.assertEqual(len(context['mylist']), 3, "The length of 'mylist' in the resulting context is not 3")
        
        self.assertEqual(len(context['mylist'][0]), 1, "The first column's length is not equal to 1")
        self.assertEqual(context['mylist'][0][0], 'hello', "'hello' was not properly sorted into the first column")
        
        self.assertEqual(len(context['mylist'][1]), 1, "The second column's length is not equal to 1")
        self.assertEqual(context['mylist'][1][0], 'there', "'there' was not properly sorted into the second column")
        
        self.assertEqual(len(context['mylist'][2]), 1, "The third column's length is not equal to 1")
        self.assertEqual(context['mylist'][2][0], 'dude', "'dude' was not properly sorted into the third column")
        
        # Unequal column distribution
        
        mylist = ['hello', 'there', 'dude']
        expr = '{% columnize mylist into 2 %}'
        rendered, context = self.render(expr, {'mylist': mylist})
        
        self.assertEqual(len(context['mylist']), 2, "The length of 'mylist' in the resulting context is not 2")
        
        self.assertEqual(len(context['mylist'][0]), 2, "The first column's length is not equal to 2")
        self.assertEqual(context['mylist'][0][0], 'hello', "'hello' was not properly sorted into the first column")
        self.assertEqual(context['mylist'][0][1], 'dude', "'dude' was not properly sorted into the first column")
        
        self.assertEqual(len(context['mylist'][1]), 1, "The second column's length is not equal to 1")
        self.assertEqual(context['mylist'][1][0], 'there', "'there' was not properly sorted into the second column")
    
    def test_as_keyword(self):
        
        mylist = ['some', 'test', 'list', 'dude']
        expr = '{% columnize mylist into 3 as differentlist %}'
        rendered, context = self.render(expr, {'mylist': mylist})
        
        self.assertEqual(context['mylist'], mylist, "The original 'mylist' differs from the context's 'mylist'")
        self.assertEqual(len(context['differentlist']), 3, "The length of 'differentlist' in the resulting context is not 3")
        
        self.assertEqual(len(context['differentlist'][0]), 2, "The first column's length is not equal to 2")
        self.assertEqual(context['differentlist'][0][0], 'some', "'some' was not properly sorted into the first column")
        self.assertEqual(context['differentlist'][0][1], 'dude', "'dude' was not properly sorted into the first column")
        
        self.assertEqual(len(context['differentlist'][1]), 1, "The second column's length is not equal to 1")
        self.assertEqual(context['differentlist'][1][0], 'test', "'test' was not properly sorted into the second column")
        
        self.assertEqual(len(context['differentlist'][2]), 1, "The third column's length is not equal to 1")
        self.assertEqual(context['differentlist'][2][0], 'list', "'test' was not properly sorted into the third column")
    
    def test_stacked_keyword(self):
        
        mylist = ['some', 'test', 'list', 'dude']
        expr = '{% columnize mylist into 3 stacked %}'
        rendered, context = self.render(expr, {'mylist': mylist})
        
        self.assertEqual(len(context['mylist']), 3, "The length of 'mylist' in the resulting context is not 3")
        
        self.assertEqual(context['mylist'][0], ['some', 'test'], "First column was not sorted properly")
        self.assertEqual(context['mylist'][1], ['list'], "Second column was not sorted properly")
        self.assertEqual(context['mylist'][2], ['dude'], "Third column was not sorted properly")
        
        # Longer list
        
        mylist = ['some', 'list', 'to', 'test', 'with', 'and', 'such', 'dude', 'awesome']
        expr = '{% columnize mylist into 4 stacked as testlist %}'
        rendered, context = self.render(expr, {'mylist': mylist})
        
        self.assertEqual(context['mylist'], mylist, "The value of 'mylist' changed in the resulting context")
        self.assertEqual(len(context['testlist']), 4, "The length of 'testlist' is incorrect")
        
        self.assertEqual(len(context['testlist'][0]), 3, "The first column's length is incorrect")
        self.assertEqual(context['testlist'][0], ['some', 'list', 'to'], "The first column was not sorted properly")
        
        self.assertEqual(len(context['testlist'][1]), 2, "The second column's length is incorrect")
        self.assertEqual(context['testlist'][1], ['test', 'with'], "The second column was not sorted properly")
        
        self.assertEqual(len(context['testlist'][2]), 2, "The third column's length is incorrect")
        self.assertEqual(context['testlist'][2], ['and', 'such'], "The third column was not sorted properly")
        
        self.assertEqual(len(context['testlist'][3]), 2, "The fourth column's length is incorrect")
        self.assertEqual(context['testlist'][3], ['dude', 'awesome'], "The fourth column was not sorted properly")


class ValueFromSettingsTestCase(TemplateTestCase):

    global_template_string = '{% load geetar %}'

    def test_basic(self):

        expr = '{% value_from_settings SECRET_KEY %}'
        rendered, context = self.render(expr)

        self.assertEqual(rendered, 'geetarT3st!')
