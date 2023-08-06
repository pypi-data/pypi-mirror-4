import os
from django.utils import unittest
from django.core.files import File
from django.forms import forms

from geetar.fields import RestrictedTypeFileField


class RestrictedTypeFileFieldTestCase(unittest.TestCase):


    def test_no_accepted_types_field(self):

        field = RestrictedTypeFileField()

        f = File(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '__init__.py')))
        f.content_type = 'image/bmp'
        data = type("",(object,),dict(file=f))

        with self.assertRaises(forms.ValidationError):
            field.clean(data, None)


    def test_unaccepted_types_field(self):

        accepted_types = ['image/bmp',]
        field = RestrictedTypeFileField(accepted_types=accepted_types)

        f = File(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '__init__.py')))
        f.content_type = 'application/exe'
        data = type("",(object,),dict(file=f, accepted_types=accepted_types))

        with self.assertRaises(forms.ValidationError):
            field.clean(data, None)


    def test_accepted_types_field(self):

        accepted_types = ['image/bmp','image/jpg', 'image/png']
        field = RestrictedTypeFileField(accepted_types=accepted_types)

        f = File(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '__init__.py')))
        f.content_type = 'image/bmp'
        data = type("",(object,),dict(file=f, accepted_types=accepted_types))

        self.assertEquals(field.clean(data, {}).file, f)

