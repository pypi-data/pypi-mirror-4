# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import random
import struct
import string
import os.path
from datetime import datetime

from oauth.oauth import OAuthToken, OAuthDataStore, OAuthConsumer

from functools import partial
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


__all__ = [
    'Token',
    'Consumer',
    'Nonce',
    'DataStore',
]


TOKEN_LENGTH = getattr(settings, 'OAUTH_TOKEN_LENGTH', 50)
TOKEN_SECRET_LENGTH = getattr(settings, 'OAUTH_TOKEN_SECRET_LENGTH', 50)
CONSUMER_SECRET_LENGTH = getattr(settings, 'OAUTH_CONSUMER_SECRET_LENGTH', 30)


def _set_seed():
    if (not hasattr(_set_seed, 'seed') and
        os.path.exists("/dev/random")):

        data = open("/dev/random").read(struct.calcsize('Q'))
        random.seed(struct.unpack('Q', data))
        _set_seed.seed = True


def generate_random_string(length):
    _set_seed()
    return ''.join(random.choice(string.ascii_letters)
                   for x in range(length))


class Token(models.Model):
    consumer = models.ForeignKey('Consumer')

    token = models.CharField(
        max_length=TOKEN_LENGTH,
        default=partial(generate_random_string, TOKEN_LENGTH),
        primary_key=True)

    token_secret = models.CharField(
        max_length=TOKEN_SECRET_LENGTH,
        default=partial(generate_random_string, TOKEN_SECRET_LENGTH))

    name = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(default=datetime.utcnow)
    updated_at = models.DateTimeField(default=datetime.utcnow)

    def oauth_token(self):
        """Return OAuthToken with information contained in this model"""
        return OAuthToken(self.token, self.token_secret)

    def serialize(self):
        return {
            'consumer_key': self.consumer.key,
            'consumer_secret': self.consumer.secret,
            'token': self.token,
            'token_secret': self.token_secret,
            'name': self.name,
            'created': str(self.created_at),
            'updated': str(self.updated_at),
        }

    def __unicode__(self):
        return self.token

    class Meta:
        db_table = 'oauth_token'


class Consumer(models.Model):
    user = models.OneToOneField(User, related_name='oauth_consumer')

    @property
    def key(self):
        return self.user.username

    secret = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default=partial(generate_random_string, CONSUMER_SECRET_LENGTH)
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.key

    def oauth_consumer(self):
        """Return OAuthConsumer based on information contained in this model"""
        return OAuthConsumer(self.key, self.secret)

    class Meta:
        db_table = 'oauth_consumer'


class Nonce(models.Model):
    token = models.ForeignKey(Token)
    consumer = models.ForeignKey(Consumer)

    nonce = models.CharField(max_length=255, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, consumer_key, token_value, nonce):
        """
        Create new nonce object linked to given consumer and token
        """
        consumer = Consumer.objects.get(
            user__username=consumer_key)
        token = consumer.token_set.get(token=token_value)
        return consumer.nonce_set.create(token=token, nonce=nonce)

    class Meta:
        db_table = 'oauth_nonce'
        unique_together = ('nonce', 'token', 'consumer')


class DataStore(OAuthDataStore):

    def lookup_token(self, token_type, token_field):
        """
        :param token_type: type of token to lookup
        :param token_field: token to look up

        :note: token_type should always be 'access' as only such tokens are
               stored in database

        :returns: OAuthToken object
        """
        assert token_type == 'access'

        try:
            token = Token.objects.get(token=token_field)
            return OAuthToken(token.token, token.token_secret)
        except Token.DoesNotExist:
            return None

    def lookup_consumer(self, consumer_key):
        """
        :param consumer_key: consumer key to lookup

        :returns: OAuthConsumer object
        """
        try:
            consumer = Consumer.objects.get(
                user__username=consumer_key)
            return consumer.oauth_consumer()
        except Consumer.DoesNotExist:
            return None

    def lookup_nonce(self, consumer, token, nonce):
        """
        :param consumer: OAuthConsumer object
        :param token: OAuthToken object
        :param nonce: nonce to check

        """
        count = Nonce.objects.filter(
            consumer__user__username=consumer.key,
            token__token=token.key,
            nonce=nonce).count()
        if count > 0:
            return True
        else:
            Nonce.create(consumer.key, token.key, nonce)
            return False

