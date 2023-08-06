from django.db import models
from django.forms import forms

class RestrictedTypeFileField(models.FileField):

    """
    Extension of FileField used to restrict to specified file types.
    accepted_types: a list of allowed content types (application/pdf, image/jpeg, image/png, etc)
    """

    def __init__(self, *args, **kwargs):

        self.accepted_types = kwargs.pop("accepted_types", [])
        super(RestrictedTypeFileField, self).__init__(*args, **kwargs)


    def clean(self, *args, **kwargs):

        data = super(RestrictedTypeFileField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if not content_type in self.accepted_types:
                raise forms.ValidationError('Filetype not supported.')
        except AttributeError:
            pass

        return data

try:
    # custom fields need to be explicitly introspected by South:
    # http://south.readthedocs.org/en/latest/customfields.html
    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([
        (
            [RestrictedTypeFileField], 
            [],         # Positional args
            {           # Kwargs
                "accepted_types": ["accepted_types", {}],
            },
        ),
    ], ["^geetar\.fields\.RestrictedTypeFileField"])
except Exception:
    pass

