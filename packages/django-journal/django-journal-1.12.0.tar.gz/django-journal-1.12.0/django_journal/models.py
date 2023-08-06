import string

from django.db import models
from django.db.models import query
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

JOURNAL_METADATA_CACHE_TIMEOUT = 3600

class CachedQuerySet(query.QuerySet):
    def get_cached(self, **kwargs):
        key = tuple(sorted(kwargs.iteritems()))
        hash1 = key.__hash__()
        hash2 = ('x', key).__hash__()
        key = 'dj-cache-%s-%s-%s' % (self.model.__name__, hash1, hash2)
        instance = cache.get(key)
        if instance is not None:
            return instance
        instance, created = self.get_or_create(**kwargs)
        if JOURNAL_METADATA_CACHE_TIMEOUT:
            cache.set(key, instance, JOURNAL_METADATA_CACHE_TIMEOUT)
        return instance


class CachedManager(models.Manager):
    def get_query_set(self):
        return CachedQuerySet(self.model, using=self._db)

    def get_cached(self, **kwargs):
        return self.get_query_set().get_cached(**kwargs)


class TagManager(CachedManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Tag(models.Model):
    '''Tag allows typing event and data linked to events.

       name:
           the string identifier of the tag
    '''
    objects = TagManager()
    name = models.CharField(max_length=32, unique=True, db_index=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Journal tag')


class TemplateManager(CachedManager):
    def get_by_natural_key(self, content):
        return self.get(content=content)


class Template(models.Model):
    '''Template for formatting an event.

       ex.: Template(
                content='{user1} gave group {group} to {user2}')
    '''
    objects = TemplateManager()
    content = models.TextField(unique=True, db_index=True)

    def __unicode__(self):
        return self.content

    def natural_key(self):
        return (self.content,)

    class Meta:
        ordering = ('content',)


class JournalManager(models.Manager):
    def get_query_set(self):
        return super(JournalManager, self).get_query_set() \
               .prefetch_related('objectdata_set__content_type',
                       'stringdata_set', 'objectdata_set__tag',
                       'stringdata_set__tag', 'objectdata_set__content_object',
                       'tag', 'template') \
               .select_related('tag', 'template')

    def for_object(self, obj, tag=None):
        '''Return Journal records linked to this object.'''
        content_type = ContentType.objects.get_for_model(obj)
        if tag is None:
            return self.filter(objectdata__content_type=content_type,
                    objectdata__object_id=obj.pk)
        else:
            return self.filter(
                    objectdata__tag__name=tag,
                    objectdata__content_type=content_type,
                    objectdata__object_id=obj.pk)

    def for_objects(self, objects):
        '''Return journal records linked to any of this objects.

           All objects must have the same model.
        '''
        if not objects:
            return self.none()
        content_types = [ ContentType.objects.get_for_model(obj)
                for obj in objects ]
        if len(set(content_types)) != 1:
            raise ValueError('objects must have of the same content type')
        pks = [ obj.pk for obj in objects ]
        return self.filter(
                objectdata__content_type=content_types[0],
                objectdata__object_id__in=pks)

    def for_tag(self, tag):
        '''Returns Journal records linked to this tag by their own tag or
           the tag on their data records.
        '''
        if not isinstance(tag, Tag):
            try:
                tag = Tag.objects.get_cached(name=tag)
            except Tag.DoesNotExist:
                return self.none()
        # always remember: multiple join (OR in WHERE) produces duplicate
        # lines ! Use .distinct() for safety.
        return self.filter(models.Q(tag=tag)|
                models.Q(objectdata__tag=tag)|
                models.Q(stringdata__tag=tag)) \
                .distinct()


class Journal(models.Model):
    '''One line of the journal.

       Each recorded event in the journal is a Journal instance.

       time - the time at which the event was recorded
       tag - the tag giving the type of event
       template - a format string to present the event
       message - a simple string representation of the event, computed using
       the template and associated datas.
    '''
    objects = JournalManager()

    time = models.DateTimeField(auto_now_add=True, db_index=True)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    message = models.CharField(max_length=128, db_index=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = _('Journal entry')
        verbose_name_plural = _('Journal entries')

    def message_context(self):
        ctx = {}
        for data in self.objectdata_set.all():
            if data.content_object is not None:
                ctx[data.tag.name] = data.content_object
            else:
                ctx[data.tag.name] = u'<deleted {content_type} {object_id}>'.format(
                        content_type=data.content_type, object_id=data.object_id)
        for data in self.stringdata_set.all():
            ctx[data.tag.name] = data.content
        for text, field, format_spec, conversion in string.Formatter().parse(self.template.content):
            if not field:
                continue
            splitted = field.split('.')
            if splitted[0] not in ctx:
                ctx[splitted[0]] = None
        return ctx

    def __unicode__(self):
        ctx = self.message_context()
        return self.template.content.format(**ctx)

    def __repr__(self):
        return '<Journal pk:{0} tag:{1} message:{2}>'.format(
                self.pk, unicode(self.tag).encode('utf-8'),
                unicode(self.message).encode('utf-8'))


class StringData(models.Model):
    '''String data associated to a recorded event.

       journal:
           the recorded event
       tag:
           the identifier for this data
       content:
           the string value of the data
    '''
    journal = models.ForeignKey(Journal)
    tag = models.ForeignKey(Tag)
    content = models.TextField()

    class Meta:
        unique_together = (('journal', 'tag'),)
        verbose_name = _('Linked text string')


class ObjectData(models.Model):
    '''Object data associated with a recorded event.

       journal:
           the recorded event
       tag:
           the identifier for this data
       content_object:
           the object value of the data
    '''
    journal = models.ForeignKey(Journal)
    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type',
            'object_id')

    class Meta:
        unique_together = (('journal', 'tag'),)
        verbose_name = _('Linked object')

    def __unicode__(self):
        return u'{0}:{1}:{2}'.format(self.journal.id, self.tag, self.content_object)
