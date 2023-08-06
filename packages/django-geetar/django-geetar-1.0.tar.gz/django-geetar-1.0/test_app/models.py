from django.db import models

from geetar.statusable.models import StatusableModel, SingleActiveModel


class Author(StatusableModel):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Book(StatusableModel):

    author = models.ForeignKey(Author)
    name = models.CharField(max_length=255)


class FeaturedAuthor(SingleActiveModel):

    author = models.ForeignKey(Author)