# -*- coding: utf-8 -*-
from django.db import models
from facebook_api.models import FacebookGraphIDModel, FacebookGraphManager
import logging

log = logging.getLogger('facebook_applications')

class Application(FacebookGraphIDModel):
    class Meta:
        verbose_name = 'Facebook application'
        verbose_name_plural = 'Facebook applications'
        ordering = ['name']

    name = models.CharField(max_length=200)
    namespace = models.CharField(max_length=100)

    objects = models.Manager()
    remote = FacebookGraphManager()

    def __unicode__(self):
        return self.name
