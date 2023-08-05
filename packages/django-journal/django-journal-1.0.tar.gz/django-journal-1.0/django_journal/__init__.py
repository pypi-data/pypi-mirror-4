from exceptions import JournalException
from models import (Journal, Tag, Template, ObjectData, StringData)

from django.db import models
from django.conf import settings

__all__ = ('record', 'error_record', 'Journal')

def unicode_truncate(s, length, encoding='utf-8'):
    '''Truncate an unicode string so that its UTF-8 encoding is less thant
       length.'''
    encoded = s.encode(encoding)[:length]
    return encoded.decode(encoding, 'ignore')

def record(tag, tpl, using='default', **kwargs):
    '''Record an event in the journal. The modification is done inside the
       current transaction.

       tag:
           a string identifier giving the type of the event
       tpl:
           a format string to describe the event
       kwargs:
           a mapping of object or data to interpolate in the format string
    '''
    tag, created = Tag.objects.using(using).get_or_create(name=tag)
    template, created = Template.objects.using(using).get_or_create(content=tpl)
    try:
        message = tpl.format(**kwargs)
    except (KeyError, IndexError), e:
        raise JournalException(
                'Missing variable for the template message', tpl, e)
    journal = Journal.objects.using(using).create(tag=tag, template=template,
            message=unicode_truncate(message, 128))
    for tag, value in kwargs.iteritems():
        tag, created = Tag.objects.using(using).get_or_create(name=tag)
        if isinstance(value, models.Model):
            journal.objectdata_set.create(tag=tag, content_object=value)
        else:
            journal.stringdata_set.create(tag=tag, content=unicode(value))
    return journal

def error_record(tag, tpl, **kwargs):
    '''Records error events.

       You must use this function when logging error events. It uses another
       database alias than the default one to be immune to transaction rollback
       when logging in the middle of a transaction which is going to
       rollback.
    '''
    return record(tag, tpl,
            using=getattr(settings, 'JOURNAL_DB_FOR_ERROR_ALIAS', 'default'),
            **kwargs)
