from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.utils import simplejson
from djangorestframework.tests.testcases import SettingsTestCase

from serene.tests.models import Brand, Product
from serene.tests.resources import BrandResource, ProductResource
from serene.views import CreatableInstanceModelView, PaginatedListOrCreateModelView


urlpatterns = patterns('',
    url(r'^brands/?$', PaginatedListOrCreateModelView.as_view(resource=BrandResource), name='brand_list_or_create'),
    url(r'^brands/(?P<id>\d+)/?$', CreatableInstanceModelView.as_view(resource=BrandResource), name='brand_instance'),
    url(r'^products/?$', PaginatedListOrCreateModelView.as_view(resource=ProductResource), name='product_list_or_create'),
    url(r'^products/(?P<id>\d+)/?$', CreatableInstanceModelView.as_view(resource=ProductResource), name='product_instance'),
)


#class TestInstanceModelView(TestCase):
#
#    def setUp(self):
#        super(TestInstanceModelView, self).setUp()
#
#    def tearDown(self):
#        if hasattr(Brand, 'get_absolute_url'): delattr(Brand, 'get_absolute_url')
#        super(TestInstanceModelView, self).tearDown()
#
#    def test_instance_model_view_without_get_absolute_url(self):
#        self.nike = Brand.objects.create(name='Nike')
#
#        r = self.client.get('/brands/%s' % self.nike.id)
#
#        self.assertEqual(r.status_code, 200)
#        self.assertEqual(simplejson.loads(r.content), {
#            'id': self.nike.id,
#            'name': 'Nike',
#            'links': {},
#        })
#
#    def test_instance_model_view_with_get_absolute_url(self):
#
#        @models.permalink
#        def get_absolute_url(self):
#            return ('brand_instance', (), {'id': self.id})
#        Brand.get_absolute_url = get_absolute_url
#
#        self.nike = Brand.objects.create(name='Nike')
#
#        r = self.client.get('/brands/%s' % self.nike.id)
#
#        self.assertEqual(r.status_code, 200)
#        self.assertEqual(simplejson.loads(r.content), {
#            'id': self.nike.id,
#            'name': 'Nike',
#            'links': {
#                'self': {
#                    'href': 'http://testserver/brands/%s' % self.nike.id,
#                    'rel': 'self',
#                    'title': 'Nike',
#                }
#            },
#        })


class TestResourceFields(SettingsTestCase):
    urls = 'serene.tests.test_views'

    def setUp(self):
        super(TestResourceFields, self).setUp()


        installed_apps = tuple(settings.INSTALLED_APPS) + ('serene.tests',)
        self.settings_manager.set(INSTALLED_APPS=installed_apps)


        self._orig_maxDiff = self.maxDiff
        self.maxDiff = None
        self._orig_ProductResource_fields = ProductResource.fields

    def tearDown(self):
        ProductResource.fields = self._orig_ProductResource_fields
        self.maxDiff = self._orig_maxDiff
        super(TestResourceFields, self).tearDown()

    def test_no_fields(self):
        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'id': self.ball.id,
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            'brand': {
                'id': self.nike.id,
                'title': 'Nike',
                'links': {
                    'self': {
                        'href': 'http://testserver/brands/%s' % self.nike.id,
                        'rel': 'self',
                        'title': 'Nike',
                        }
                }
            },
            'links': {
                'self': {
                    'href': 'http://testserver/products/%s' % self.ball.id,
                    'rel': 'self',
                    'title': 'Nike Speed',
                    },
                'brand': {
                    'href': 'http://testserver/brands/%s' % self.nike.id,
                    'rel': 'brand',
                    'title': 'Nike',
                    }
            }
        })

    def test_fields(self):
        ProductResource.fields = ('name', 'code', 'color', 'last_modified')

        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            })

    def test_fields_with_links(self):
        ProductResource.fields = ('name', 'code', 'color', 'last_modified', 'links')

        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            'links': {
                'self': {
                    'href': 'http://testserver/products/%s' % self.ball.id,
                    'rel': 'self',
                    'title': 'Nike Speed',
                    },
                'brand': {
                    'href': 'http://testserver/brands/%s' % self.nike.id,
                    'rel': 'brand',
                    'title': 'Nike',
                    }
            }
        })

    def test_fields_with_related_object(self):
        ProductResource.fields = ('name', 'code', 'color', 'last_modified', 'brand')

        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            'brand': {
                'id': self.nike.id,
                'title': 'Nike',
                'links': {
                    'self': {
                        'href': 'http://testserver/brands/%s' % self.nike.id,
                        'rel': 'self',
                        'title': 'Nike',
                        }
                }
            }
        })

    def test_subfields_with_links(self):
        ProductResource.fields = ('name', 'code', 'color', 'last_modified', ('links', ('self',)))

        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            'links': {
                'self': {
                    'href': 'http://testserver/products/%s' % self.ball.id,
                    'rel': 'self',
                    'title': 'Nike Speed',
                    }
            }
        })

    def test_subfields_with_related_object(self):
        ProductResource.fields = ('name', 'code', 'color', 'last_modified', ('brand', ('id', 'title', 'links', 'name', 'code')))

        self.nike = Brand.objects.create(name='Nike', code='NK')
        self.ball = Product.objects.create(name='Nike Speed', code='NKSP01', color='Black and White', brand=self.nike)

        response = self.client.get('/products/%s' % self.ball.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(simplejson.loads(response.content), {
            'name': 'Nike Speed',
            'code': 'NKSP01',
            'color': 'Black and White',
            'last_modified': self.ball.last_modified.isoformat(),
            'brand': {
                'id': self.nike.id,
                'title': 'Nike',
                'links': {
                    'self': {
                        'href': 'http://testserver/brands/%s' % self.nike.id,
                        'rel': 'self',
                        'title': 'Nike',
                        }
                },
                'name': 'Nike',
                'code': 'NK',
                },
            })