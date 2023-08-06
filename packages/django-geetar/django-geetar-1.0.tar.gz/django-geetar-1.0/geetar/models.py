from django.db import models

from statusable.models import StatusableModel


class GeetarBaseModel(StatusableModel):

    """
    Handy base model with status and date info, would likely serve well
    as a base model in most cases
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
