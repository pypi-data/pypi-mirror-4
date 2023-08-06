from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

# TODO: Refactor this into a generic utils app to remove the wells dep
from armstrong.core.arm_wells.querysets import GenericForeignKeyQuerySet


class Series(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    slug = models.SlugField()

    def __unicode__(self):
        return self.title

    def get_items(self):
        return GenericForeignKeyQuerySet(self.nodes.all().select_related())

    @property
    def items(self):
        if not getattr(self, '_items', False):
            self._items = self.get_items()
        return self._items


class SeriesNode(models.Model):
    class Meta:
        ordering = ['order', ]

    series = models.ForeignKey(Series, related_name='nodes')

    order = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
