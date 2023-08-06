from django.db import models


"""
Base model and accompanying QuerySet and Manager for 'statusable' models.
Adds a 'status' field to the model along with
"""


STATUS_INACTIVE = 1
STATUS_ACTIVE = 2
STATUS_CHOICES = (
    (STATUS_INACTIVE, 'Inactive',),
    (STATUS_ACTIVE, 'Active',),
)


class StatusableQuerySet(models.query.QuerySet):

    """
    QuerySet class for statusable objects with some handy shortcut queries
    """

    def inactive(self):
        return self.filter(status=STATUS_INACTIVE)

    def deactivate(self):
        return self.update(status=STATUS_INACTIVE)

    def active(self):
        return self.filter(status=STATUS_ACTIVE)

    def activate(self):
        return self.update(status=STATUS_ACTIVE)


class StatusableManager(models.Manager):

    """
    Object manager to be paired with StatusableModel to add a few handy query
    shortcuts. This manager needs to work as a proxy for any custom QuerySet
    methods so that chaining is still possible.
    """

    def get_query_set(self):
        return StatusableQuerySet(self.model, using=self._db)

    def inactive(self):
        return self.get_query_set().inactive()

    def deactivate(self):
        return self.get_query_set().deactivate()

    def active(self):
        return self.get_query_set().active()

    def activate(self):
        return self.get_query_set().activate()


class StatusableModel(models.Model):

    """
    Base model for models that require status-able state
    """

    objects = StatusableManager()

    status = models.IntegerField(db_index=True, choices=STATUS_CHOICES,
                                 default=STATUS_INACTIVE)

    class Meta:
        abstract = True

    def deactivate(self, save=True):
        self.status = STATUS_INACTIVE
        if save:
            self.save()

    def activate(self, save=True):
        self.status = STATUS_ACTIVE
        if save:
            self.save()

    @property
    def is_inactive(self):
        return not self.is_active

    @property
    def is_active(self):
        return self.status == STATUS_ACTIVE


class SingleActiveQuerySet(StatusableQuerySet):

    """
    Make sure that when records are bulk activated, only 1 is actually
    activated
    """

    def active(self):
        return self.get(status=STATUS_ACTIVE)

    def activate(self):

        """
        If this QuerySet contains multiple records, just pull off the first
        and activate it
        """

        rows = self.all()
        if len(rows):
            active = rows[0]
            return active.activate()
        return 0


class SingleActiveManager(StatusableManager):

    """
    Simply setting the SingleActiveQuerySet
    """

    def get_query_set(self):
        return SingleActiveQuerySet(self.model, using=self._db)


class SingleActiveModel(StatusableModel):

    """
    Extension of the statusable model that only allows one record to be active
    at a time
    """

    objects = SingleActiveManager()

    # Optional list of fields to make active status unique with

    _active_with_fields = []

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        """
        After save, if this record is active, deactivate all others
        """

        super(SingleActiveModel, self).save(*args, **kwargs)

        if self.status == STATUS_ACTIVE:
            active = self.__class__.objects.filter(status=STATUS_ACTIVE).exclude(pk=self.pk)
            if self._active_with_fields:
                filters = {}
                for field in self._active_with_fields:
                    filters[field] = getattr(self, field)
                active = active.filter(**filters)
            active.deactivate()
