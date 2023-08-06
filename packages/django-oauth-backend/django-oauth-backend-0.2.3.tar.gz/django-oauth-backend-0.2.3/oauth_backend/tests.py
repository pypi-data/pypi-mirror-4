# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from django.db import IntegrityError
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Consumer, DataStore, Nonce, Token, OAuthToken


class BaseTestCase(TestCase):

    @property
    def user(self):
        if not hasattr(self, '_user'):
            self._user = User.objects.create_user(
                'test_username', 'test@canonical.com', 'password'
            )
        return self._user


class TokenTestCase(BaseTestCase):

    def setUp(self):
        super(TokenTestCase, self).setUp()
        self.consumer, _ = Consumer.objects.get_or_create(user=self.user)
        self.token = Token(consumer=self.consumer, token='token',
                           token_secret='secret', name='name')

    def test_unicode(self):
        self.assertEqual(unicode(self.token), u'token')

    def test_serialize(self):
        expected = {'consumer_key': self.consumer.key,
                    'consumer_secret': self.consumer.secret,
                    'token': self.token.token,
                    'token_secret': self.token.token_secret,
                    'name': self.token.name,
                    'created': str(self.token.created_at),
                    'updated': str(self.token.updated_at)}
        self.assertEqual(self.token.serialize(), expected)


class ConsumerTestCase(BaseTestCase):

    def test_unicode(self):
        consumer, _ = Consumer.objects.get_or_create(user=self.user)
        self.assertEqual(unicode(consumer),
                         unicode(self.user.username))

    def test_one_to_one_relationship_with_user(self):
        consumer, _ = Consumer.objects.get_or_create(user=self.user)

        self.assertEquals(self.user.id, consumer.user.id)
        self.assertEquals(consumer.id, self.user.oauth_consumer.id)


class NonceTestCase(BaseTestCase):

    def setUp(self):
        super(NonceTestCase, self).setUp()
        self.consumer = Consumer.objects.create(user=self.user)
        self.token = Token.objects.create(
            consumer=self.consumer, token='token', token_secret='secret',)

    def test_different_nonce_for_same_token_same_consumer(self):
        Nonce.create(self.consumer.key, self.token.token, '123456')
        Nonce.create(self.consumer.key, self.token.token, '123457')

    def test_same_nonce_for_same_token_same_consumer(self):
        nonce = '123456'
        Nonce.create(self.consumer.key, self.token.token, nonce)
        self.assertRaises(IntegrityError, Nonce.create,
                          self.consumer.key, self.token.token, nonce)

    def test_same_nonce_for_different_token(self):
        nonce = '123456'

        Nonce.create(self.consumer.key, self.token.token, nonce)

        token = Token.objects.create(consumer=self.consumer, token='token2',
                                     token_secret='secret', name='name')
        Nonce.create(self.consumer.key, token.token, nonce)

    def test_same_nonce_for_different_consumer(self):
        nonce = '123456'

        Nonce.create(self.consumer.key, self.token.token, nonce)

        user = User.objects.create_user('other', 'foo@example.com', 'default')
        consumer = Consumer.objects.create(user=user)
        self.token.consumer = consumer
        self.token.save()
        Nonce.create(consumer.key, self.token.token, nonce)


class DataStoreTestCase(BaseTestCase):

    def setUp(self):
        self.ds = DataStore()
        self.consumer, _ = Consumer.objects.get_or_create(user=self.user)
        self.token, _ = Token.objects.get_or_create(consumer=self.consumer,
            token='token', token_secret='secret', name='name')
        self.nonce, _ = Nonce.objects.get_or_create(consumer=self.consumer,
            token=self.token, nonce='nonce')

    def test_lookup_token_wrong_type(self):
        self.assertRaises(AssertionError, self.ds.lookup_token, 'value',
                          'token')

    def test_lookup_token_exists(self):
        # create a token
        token = self.ds.lookup_token('access', 'token')
        self.assertEqual(token.key, 'token')
        self.assertEqual(token.secret, 'secret')

    def test_lookup_token_not_exists(self):
        self.token.delete()
        token = self.ds.lookup_token('access', 'token')
        self.assertEqual(token, None)

    def test_lookup_consumer_exists(self):
        consumer_key = self.consumer.key
        result = self.ds.lookup_consumer(consumer_key)
        self.assertEqual(result.key, self.consumer.key)
        self.assertEqual(result.secret, self.consumer.secret)

    def test_lookup_consumer_not_exists(self):
        consumer_key = 'foo'
        consumer = self.ds.lookup_consumer(consumer_key)
        self.assertEqual(consumer, None)

    def test_lookup_nonce_exists(self):
        otoken = OAuthToken(self.token.token, self.token.token_secret)
        r = self.ds.lookup_nonce(self.consumer, otoken, 'nonce')
        self.assertTrue(r)

    def test_lookup_nonce_not_exists(self):
        self.nonce.delete()
        otoken = OAuthToken(self.token.token, self.token.token_secret)
        r = self.ds.lookup_nonce(self.consumer, otoken, 'nonce')
        self.assertFalse(r)
