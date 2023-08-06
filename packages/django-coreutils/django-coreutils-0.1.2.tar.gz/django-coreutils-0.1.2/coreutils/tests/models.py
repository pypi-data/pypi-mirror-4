# coding: utf8

from django.contrib.auth.models import Group, User

from testutils import BaseTestCase

from ..models import (
    get_identifier,
    get_model_identifier,
    get_model_class,
    is_valid_identifier,
    translate_identifier
)


class TestModels(BaseTestCase):
    def setUp(self):
        self.group = Group(pk=1)
        self.user = User(pk=1)

    def test_get_identifier(self):
        self.assertEquals(get_identifier(self.group), 'auth.Group:1')
        self.assertEquals(get_identifier(self.user), 'auth.User:1')

    def test_is_valid_identifier_valid(self):
        self.assertTrue(is_valid_identifier('str.str:data'))
        self.assertTrue(is_valid_identifier('auth.Group:1'))
        self.assertTrue(is_valid_identifier('auth.User:1'))

    def test_is_valid_identifier_empty(self):
        self.assertFalse(is_valid_identifier(''))
        self.assertFalse(is_valid_identifier(None))

    def test_is_valid_identifier_invalid(self):
        self.assertFalse(is_valid_identifier('str.str:'))
        self.assertFalse(is_valid_identifier('str.:data'))
        self.assertFalse(is_valid_identifier('auth.:1'))
        self.assertFalse(is_valid_identifier('.User:1'))
        self.assertFalse(is_valid_identifier('auth.User1'))
        self.assertFalse(is_valid_identifier('.User1'))
        self.assertFalse(is_valid_identifier('.:'))

    def test_get_model_identifier(self):
        self.assertEquals(get_model_identifier(self.group), 'auth.Group')
        self.assertEquals(get_model_identifier(self.user), 'auth.User')

    def test_get_model_class(self):
        self.assertEquals(
            self.group.__class__, get_model_class('auth.Group')
        )

        self.assertEquals(
            self.user.__class__, get_model_class('auth.User')
        )

    def test_translate_identifier_no_query(self):
        self.assertEquals(
            (self.group.__class__, 1), translate_identifier('auth.Group:1')
        )

        self.assertEquals(
            (self.user.__class__, 1), translate_identifier('auth.User:1')
        )
