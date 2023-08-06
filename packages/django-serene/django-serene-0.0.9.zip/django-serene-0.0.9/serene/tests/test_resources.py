"""Tests for the resource module"""
from django.test import TestCase

from serene import models
from serene.resources import ModelResource


class TestExtraFields(TestCase):
    """
    Test extra fields (i.e. links, title) in the ModelResource class
    """

    def setUp(self):
        super(TestExtraFields, self).setUp()

        class M7(models.Model):
            field1 = models.CharField(max_length=256)
            field2 = models.CharField(max_length=256)

            def __unicode__(self):
                return '%s %s' % (self.field1, self.field2)

        class M8(models.Model):
            field1 = models.CharField(max_length=256)
            field2 = models.CharField(max_length=256)

            def __unicode__(self):
                return '%s %s' % (self.field1, self.field2)

            def get_absolute_url(self):
                return '/m8s/%s' % self.id

        class M9(models.Model):
            field1 = models.ForeignKey(M7)
            field2 = models.ForeignKey(M8)

        self.M7 = M7
        self.m7 = M7(field1='foo', field2='bar')
        self.m8 = M8(field1='joe', field2='smith')
        self.m9 = M9(field1=self.m7, field2=self.m8)

    def test_links(self):
        """
        Test 'links' field
        """
        self.M7.get_absolute_url = lambda self: '/m7s/%s' % self.id

        class ResourceM1(ModelResource):
            pass

        self.assertEqual(ResourceM1().serialize(self.m7), {
            'id': self.m7.id,
            'field1': u'foo',
            'field2': u'bar',
            'last_modified': self.m7.last_modified,
            'links': {
                'self': {
                    'href': u'/m7s/%s' % self.m7.id,
                    'rel': u'self',
                    'title': u'foo bar'
                }
            }
        })

        del self.M7.get_absolute_url

    def test_skip_links(self):
        """
        Test 'links' field should be skipped if 'get_absolute_url' is not defined in the model
        """
        class ResourceM1(ModelResource):
            pass

        self.assertEqual(ResourceM1().serialize(self.m7), {
            'id': self.m7.id,
            'field1': u'foo',
            'field2': u'bar',
            'last_modified': self.m7.last_modified,
        })

    def test_links_with_related_object(self):
        """
        Test 'links' field should include related objects only if get_absolute_url is implemented.
        """
        class ResourceM3(ModelResource):
            fields = ('links',)

        self.assertEqual(ResourceM3().serialize(self.m9), {
            'links': {
                'field2': {
                    'href': '/m8s/%s' % self.m8.id,
                    'rel': 'field2',
                    'title': 'joe smith'
                }
            }
        })
