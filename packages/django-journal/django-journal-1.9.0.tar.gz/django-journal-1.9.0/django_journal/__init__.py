import logging

from exceptions import JournalException
from models import (Journal, Tag, Template)


from django.db import models, transaction
from django.conf import settings

__all__ = ('record', 'error_record', 'Journal')

def unicode_truncate(s, length, encoding='utf-8'):
    '''Truncate an unicode string so that its UTF-8 encoding is less than
       length.'''
    encoded = s.encode(encoding)[:length]
    return encoded.decode(encoding, 'ignore')


__TAG_CACHE = dict()


def get_tag(name, using=None):
    if name not in __TAG_CACHE:
        __TAG_CACHE[name], created = \
                Tag.objects.using(using).get_or_create(name=name)
    return __TAG_CACHE[name]


__TEMPLATE_CACHE = dict()


def get_template(content, using=None):
    if content not in __TEMPLATE_CACHE:
        __TEMPLATE_CACHE[content], created = \
                Template.objects.using(using).get_or_create(content=content)
    return __TEMPLATE_CACHE[content]


def record(tag, template, using=None, **kwargs):
    '''Record an event in the journal. The modification is done inside the
       current transaction.

       tag:
           a string identifier giving the type of the event
       tpl:
           a format string to describe the event
       kwargs:
           a mapping of object or data to interpolate in the format string
    '''
    try:
        sid = transaction.savepoint()
        template = unicode(template)
        tag = get_tag(tag, using=using)
        template = get_template(template, using=using)
        try:
            message = template.content.format(**kwargs)
        except (KeyError, IndexError), e:
            raise JournalException(
                    'Missing variable for the template message', template, e)
        try:
            logger = logging.getLogger('django.journal.%s' % tag)
            if tag.name == 'error':
                logger.error(message)
            else:
                logger.info(message)
        except:
            try:
                logging.getLogger('django.journal').exception('Unable to log msg')
            except:
                pass # we tried, really, we tried
        journal = Journal.objects.using(using).create(tag=tag, template=template,
                message=unicode_truncate(message, 128))
        for tag, value in kwargs.iteritems():
            if value is None:
                continue
            tag = get_tag(tag, using=using)
            if isinstance(value, models.Model):
                journal.objectdata_set.create(tag=tag, content_object=value)
            else:
                journal.stringdata_set.create(tag=tag, content=unicode(value))
        transaction.savepoint_commit(sid)
        return journal
    except:
        transaction.savepoint_rollback(sid)

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
