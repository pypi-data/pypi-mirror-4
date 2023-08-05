from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class MigratedObjectManager(models.Manager):

    def last_migration(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(
            content_type=ctype,
            object_id=obj.pk,
        ).latest('migration_date')


class MigratedObject(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    object_name = models.CharField(null=True, db_index=True, max_length=200)
    object_url = models.CharField(null=True, db_index=True, max_length=200)
    old_db_key = models.CharField(null=True, db_index=True, max_length=100)
    migration_command = models.CharField(verbose_name=_('migration command'),
                                         null=True, db_index=True, max_length=200)
    migration_date = models.DateTimeField(verbose_name=_('last migration date'),
                                          null=True)
    is_migrating = models.BooleanField(verbose_name=_('is migrating'),
                                       default=False)
    is_created = models.BooleanField(verbose_name=_('is created'),
                                     default=False)
    migration_fields_used = models.TextField(null=True)
    has_errors = models.BooleanField(verbose_name=_('has errors'),
                                     default=False)
    errors = models.TextField(default='')

    objects = MigratedObjectManager()

    class Meta:
        verbose_name = _('migrated item')
        verbose_name_plural = _('migrated items')
        ordering = ('-migration_date', )

    def __unicode__(self):
        return u'Migrated object "%s" from id "%s"' % (self.object_name, self.old_db_key)

    def save(self, *args, **kwargs):
        if hasattr(self, '_object_cache'):
            del self._object_cache  # force object reloading
        self.object_name = unicode(self.object)[:200]
        if hasattr(self.object, 'get_absolute_url'):
            self.object_url = self.object.get_absolute_url()
        super(MigratedObject, self).save(*args, **kwargs)
