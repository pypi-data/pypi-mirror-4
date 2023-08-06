"""Tests for the resource module"""
import datetime
import decimal

from django.test import TestCase
from django.utils.translation import ugettext_lazy

from serene import models
from serene.serializers import RelatedSerializer, Serializer


class TestObjectToData(TestCase):
    """
    Tests for the Serializer class.
    """

    class GMT1(datetime.tzinfo):
        """Simeple tzinfo class for testing"""
        def __init__(self):                         # DST starts last Sunday in March
            year = datetime.date.today().year
            d = datetime.datetime(year, 4, 1)    # ends last Sunday in October
            self.dston = d - datetime.timedelta(days=d.weekday() + 1)
            d = datetime.datetime(year, 11, 1)
            self.dstoff = d - datetime.timedelta(days=d.weekday() + 1)
        def utcoffset(self, dt):
            return datetime.timedelta(hours=1) + self.dst(dt)
        def dst(self, dt):
            if self.dston <=  dt.replace(tzinfo=None) < self.dstoff:
                return datetime.timedelta(hours=1)
            else:
                return datetime.timedelta(0)
        def tzname(self,dt):
            return "GMT +1"


    def setUp(self):
        super(TestObjectToData, self).setUp()
        self.serializer = Serializer()
        self.serialize = self.serializer.serialize

    def test_decimal(self):
        """Decimals need to be converted to a string representation."""
        self.assertEquals(self.serialize(decimal.Decimal('1.5')), decimal.Decimal('1.5'))

    def test_function(self):
        """Functions with no arguments should be called."""
        def foo():
            return 1
        self.assertEquals(self.serialize(foo), 1)

    def test_method(self):
        """Methods with only a ``self`` argument should be called."""
        class Foo(object):
            def foo(self):
                return 1
        self.assertEquals(self.serialize(Foo().foo), 1)

    def test_date(self):
        """date objects need to be converted to ISO format."""
        today = datetime.date.today()
        self.assertEquals(self.serialize(today), today.isoformat())

    def test_datetime(self):
        """datetime objects need to be converted to ISO format."""
        now = datetime.datetime.now()   # naive datetime i.e. no tzinfo
        self.assertEquals(self.serialize(now), now.isoformat())
        now = datetime.datetime.now(tz=self.GMT1()) # aware datetime i.e. with tzinfo
        self.assertEquals(self.serialize(now), now.isoformat())

    def test_time(self):
        """time objects need to be converted to ISO format."""
        time = datetime.datetime.now().time()   # naive time i.e. no tzinfo
        self.assertEquals(self.serialize(time), time.isoformat())

    def test_dict_method_name_collision(self):
        """dict with key that collides with dict method name"""
        self.assertEquals(self.serialize({'items': 'foo'}), {'items': u'foo'})
        self.assertEquals(self.serialize({'keys': 'foo'}), {'keys': u'foo'})
        self.assertEquals(self.serialize({'values': 'foo'}), {'values': u'foo'})

    def test_ugettext_lazy(self):
        self.assertEquals(self.serialize(ugettext_lazy('foobar')), u'foobar')


class TestFieldNesting(TestCase):
    """
    Test nesting the fields in the Serializer class
    """
    def setUp(self):
        super(TestFieldNesting, self).setUp()
        self.serializer = Serializer()
        self.serialize = self.serializer.serialize

        class M1(models.Model):
            field1 = models.CharField(max_length=256)
            field2 = models.CharField(max_length=256)

        class M2(models.Model):
            field = models.OneToOneField(M1)

        class M3(models.Model):
            field = models.ForeignKey(M1)

        self.m1 = M1(field1='foo', field2='bar')
        self.m2 = M2(field=self.m1)
        self.m3 = M3(field=self.m1)


    def test_tuple_nesting(self):
        """
        Test tuple nesting on `fields` attr
        """
        class SerializerM2(Serializer):
            fields = (('field', ('field1',)),)

        class SerializerM3(Serializer):
            fields = (('field', ('field2',)),)

        self.assertEqual(SerializerM2().serialize(self.m2), {'field': {'field1': u'foo'}})
        self.assertEqual(SerializerM3().serialize(self.m3), {'field': {'field2': u'bar'}})


    def test_include_tuple_nesting(self):
        """
        Test tuple nesting on `include` attr
        """
        class SerializerM2(Serializer):
            exclude = ('id', 'field')
            include = ('field_x', ('field_y', ('field1',)))

            def field_x(self, instance):
                return '%s %s' % (instance.field.field1, instance.field.field2)

            def field_y(self, instance):
                return instance.field

        class SerializerM3(Serializer):
            exclude = ('id', 'field')
            include = ('field_x', ('field_y', ('field1',)))

            def field_x(self, instance):
                return '%s %s' % (instance.field.field1, instance.field.field2)

            def field_y(self, instance):
                return instance.field

        self.assertEqual(SerializerM2().serialize(self.m2), {
            'last_modified': None,
            'field_x': u'foo bar',
            'field_y': {
                'field1': u'foo',
            },
        })
        self.assertEqual(SerializerM3().serialize(self.m3), {
            'last_modified': None,
            'field_x': u'foo bar',
            'field_y': {
                'field1': u'foo',
            },
        })


    def test_serializer_class_nesting(self):
        """
        Test related model serialization
        """
        class NestedM2(Serializer):
            fields = ('field1', )

        class NestedM3(Serializer):
            fields = ('field2', )

        class SerializerM2(Serializer):
            fields = [('field', NestedM2)]

        class SerializerM3(Serializer):
            fields = [('field', NestedM3)]

        self.assertEqual(SerializerM2().serialize(self.m2), {'field': {'field1': u'foo'}})
        self.assertEqual(SerializerM3().serialize(self.m3), {'field': {'field2': u'bar'}})

    def test_serializer_classname_nesting(self):
        """
        Test related model serialization
        """
        class SerializerM2(Serializer):
            fields = [('field', 'NestedM2')]

        class SerializerM3(Serializer):
            fields = [('field', 'NestedM3')]

        class NestedM2(Serializer):
            fields = ('field1', )

        class NestedM3(Serializer):
            fields = ('field2', )

        self.assertEqual(SerializerM2().serialize(self.m2), {'field': {'field1': u'foo'}})
        self.assertEqual(SerializerM3().serialize(self.m3), {'field': {'field2': u'bar'}})

    def test_serializer_overridden_hook_method(self):
        """
        Test serializing a model instance which overrides a class method on the
        serializer.  Checks for correct behaviour in odd edge case.
        """
        class SerializerM2(Serializer):
            fields = ('overridden', )

            def overridden(self):
                return False

        self.m2.overridden = True
        self.assertEqual(SerializerM2().serialize_model(self.m2),
                {'overridden': True})


class TestExtraFields(TestCase):
    """
    Test extra fields (i.e. links, title) in the Serializer class
    """

    def setUp(self):
        super(TestExtraFields, self).setUp()
        self.serializer = Serializer()
        self.serialize = self.serializer.serialize

        class M1(models.Model):
            field1 = models.CharField(max_length=256)
            field2 = models.CharField(max_length=256)

            def __unicode__(self):
                return '%s %s' % (self.field1, self.field2)

        self.M1 = M1
        self.m1 = M1(field1='foo', field2='bar')

    def test_links(self):
        """
        Test 'links' field
        """
        self.M1.get_absolute_url = lambda self: '/m1s/%s' % self.id

        class SerializerM1(Serializer):
            fields = ('field1', 'links')

        self.assertEqual(SerializerM1().serialize(self.m1), {
            'field1': u'foo',
            'links': {
                'self': {
                    'href': u'/m1s/%s' % self.m1.id,
                    'rel': u'self',
                    'title': u'foo bar'
                }
            }
        })

        del self.M1.get_absolute_url

    def test_skip_links(self):
        """
        Test 'links' field should be skipped if 'get_absolute_url' is not defined in the model
        """
        class SerializerM1(Serializer):
            fields = ('field1', 'links')

        self.assertEqual(SerializerM1().serialize(self.m1), {'field1': u'foo'})

    def test_title(self):
        """
        Test 'links' field
        """
        class SerializerM1(Serializer):
            fields = ('field1', 'title')

        self.assertEqual(SerializerM1().serialize(self.m1), {'field1': u'foo', 'title': u'foo bar'})


class TestRelatedSerializer(TestCase):
    """
    Test the default RelatedSerializer class
    """
    def setUp(self):
        super(TestRelatedSerializer, self).setUp()
        self.serializer = Serializer()
        self.serialize = self.serializer.serialize

        class M4(models.Model):
            field1 = models.CharField(max_length=256)
            field2 = models.CharField(max_length=256)

            def __unicode__(self):
                return '%s %s' % (self.field1, self.field2)

            def get_absolute_url(self):
                return '/m1s/%s' % self.id

        class M5(models.Model):
            field = models.OneToOneField(M4)

        class M6(models.Model):
            field = models.ForeignKey(M4)

        self.m1 = M4(id=1, field1='foo', field2='bar')
        self.m2 = M5(id=2, field=self.m1)
        self.m3 = M6(id=3, field=self.m1)

    def test_serialize_related_model(self):
        """
        Test serialize related model
        """
        class SerializerM2(Serializer):
            related_serializer = RelatedSerializer

        class SerializerM3(Serializer):
            related_serializer = RelatedSerializer

        self.assertEqual(SerializerM2().serialize(self.m2), {
            'id': self.m2.id,
            'field': {
                'id': self.m1.id,
                'title': u'foo bar',
                'links': {
                    'self': {
                        'href': u'/m1s/%s' % self.m1.id,
                        'rel': u'self',
                        'title': u'foo bar'
                    }
                }
            },
            'last_modified': None,
        })

        self.assertEqual(SerializerM3().serialize(self.m3), {
            'id': self.m3.id,
            'field': {
                'id': self.m1.id,
                'title': u'foo bar',
                'links': {
                    'self': {
                        'href': u'/m1s/%s' % self.m1.id,
                        'rel': u'self',
                        'title': u'foo bar'
                    }
                }
            },
            'last_modified': None,
        })

    def test_serialize_related_dict(self):
        """
        Test serialize related dict
        """
        class SerializerM1(Serializer):
            fields = ('links',)
            related_serializer = RelatedSerializer

        self.assertEqual(SerializerM1().serialize(self.m1), {
            'links': {
                'self': {
                    'href': u'/m1s/%s' % self.m1.id,
                    'rel': u'self',
                    'title': u'foo bar'
                }
            }
        })

    def test_serialize_related_dict_has_links_already(self):
        """
        Test serializing related dict that already has links in it
        """
        class SerializerDict(Serializer):
            fields = ('links',)
            related_serializer = RelatedSerializer

        instance_with_links = {
            'links': {
                'self': {
                    'href': 'http://testserver/m1'
                }
            }
        }

        self.assertEqual(SerializerDict().serialize(instance_with_links), instance_with_links)