"""Tests for the templatetags of the ``subscriptions`` app."""
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ..templatetags.subscribe_tags import (
    get_ctype,
    get_subscribers,
    is_subscribed,
)
from .factories import DummyModelFactory, SubscriptionFactory


class GetCtypeTestCase(TestCase):
    """Tests for the ``get_ctype`` templatetag."""
    def test_tag(self):
        dummy = DummyModelFactory()
        ctype = ContentType.objects.get_for_model(dummy)
        result = get_ctype(dummy)
        self.assertEqual(result, ctype)


class GetSubscribersTestCase(TestCase):
    """Tests for the ``get_subscribers`` templatetag."""
    def test_tag(self):
        # Two subscriptions for the same thing
        sub1 = SubscriptionFactory()
        SubscriptionFactory(content_object=sub1.content_object)

        # One subscription for another thing
        SubscriptionFactory()

        result = get_subscribers(sub1.content_object)
        self.assertEqual(result.count(), 2)


class IsSubscribedTestCase(TestCase):
    """Tests for the ``is_subscribed`` templatetag."""
    def test_is_subscribed(self):
        sub = SubscriptionFactory()
        result = is_subscribed(sub.user, sub.content_object)
        self.assertTrue(result)

    def test_is_not_subscribed(self):
        sub1 = SubscriptionFactory()
        sub2 = SubscriptionFactory()
        result = is_subscribed(sub1.user, sub2.content_object)
        self.assertFalse(result)
