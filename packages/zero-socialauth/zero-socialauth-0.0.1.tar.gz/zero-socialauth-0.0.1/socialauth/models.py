# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class AuthMeta(models.Model):
    """Metadata for Authentication"""
    def __unicode__(self):
        return '%s - %s' % (self.username, self.provider)

    user = models.ForeignKey(User, related_name='authmeta')
    provider = models.CharField(max_length=255)
    is_email_filled = models.BooleanField(default=False)
    is_profile_modified = models.BooleanField(default=False)


class FacebookUserProfile(models.Model):
    """
    For users who login via Facebook.
    """
    facebook_uid = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='facebook')
    url = models.URLField(null=True)
    
    def __unicode__(self):
        return "%s's profile" % self.user.username
