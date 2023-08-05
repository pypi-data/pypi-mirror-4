# -*- coding: utf-8 -*-

import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


def source_path(instance, filename, date=None):
    """
    Return path to uploaded source file.

    You can use it without setting of date - in that
    case date will set to today.
    >>> from datetime import datetime
    >>> date = datetime(2012, 9, 8)

    Function changes filename through slugify.
    >>> source_path(None, 'Zdrojovy Kod.pas', date)
    u'sources/2012/9/zdrojovy-kod.pas'
    >>> source_path(None, 'Nejlepší řešení na.světe.c', date)
    u'sources/2012/9/nejlepsi-reseni-nasvete.c'
    """

    if not date:
        date = datetime.now()

    name, ext = filename.rsplit('.', 1)
    filename = slugify(name) + '.' + ext

    return os.path.join('sources', str(date.year), \
            str(date.month), filename)


class Source(models.Model):
    user = models.ForeignKey(User)

    language = models.ForeignKey('Language')
    source = models.FileField(upload_to=source_path)

    last_upload = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.source.name


class Language(models.Model):
    name = models.CharField(max_length=20)

    cmd_compiler = models.TextField()
    cmd_starter = models.TextField()

    def __unicode__(self):
        return self.name


class LanguageExtension(models.Model):
    language = models.ForeignKey('Language')
    extension = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.extension
