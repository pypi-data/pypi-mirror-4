from django.template import Context, Template
from django.utils import unittest


class TemplateTestCase(unittest.TestCase):
    
    """
    Base test case for template stuff with some handy render shortcuts
    """
    
    global_template_string = '' # Optional template string to include with all renders, good for calling {% load ... %} and such
    
    def render(self, template, context={}):

        """
        Returns render result and context from passed in template string and context
        
            `template`  string/list/tuple   String or strings to be rendered as a template
            `context`   dict                Context variables to render into template
        
        """
        
        strings = [self.global_template_string]
        
        if type(template) in (list, tuple):
            strings.extend(list(template))
        else:
            strings.append(template)
        
        template = ''.join(strings)
        
        rendered = Template(template).render(Context(context))
        
        return rendered, context

    def render_template(self, template, context={}):
        
        """
        Returns just the render result of a template string and context combination
        
            `template`  string/list/tuple   String or strings to be rendered as a template
            `context`   dict                Context variables to render into template
        
        """
        
        rendered, context = self.render(template, context)
        return rendered