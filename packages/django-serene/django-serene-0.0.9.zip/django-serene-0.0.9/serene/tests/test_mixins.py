from datetime import datetime
import time

from django.conf import settings
from django.test.client import RequestFactory
from django.utils import simplejson as json
from django.utils.http import parse_http_date
from django.utils.unittest.case import TestCase
from djangorestframework.response import ErrorResponse
from djangorestframework.tests.testcases import SettingsTestCase
from djangorestframework.views import View

from serene import mixins
from serene.mixins import ReadModelMixin, UpdateModelMixin, UpdateOrCreateModelMixin, CreateModelMixin, PaginatorMixin
from serene.resources import ModelResource
from serene.tests.datetimestub import DatetimeStub
from serene.tests.models import DummyModel, DummierModel


class TestMixinsBase(SettingsTestCase):
    def setUp(self):
        super(TestMixinsBase, self).setUp()
        installed_apps = tuple(settings.INSTALLED_APPS) + ('serene.tests',)
        self.settings_manager.set(INSTALLED_APPS=installed_apps)
        self.req = RequestFactory()

class TestReadMixin(TestMixinsBase):

    def setUp(self):
        super(TestReadMixin, self).setUp()
        mixins.datetime = DatetimeStub()
        mixins.datetime.now = lambda: datetime(2012, 12, 12, 6, 6, 6)

    def tearDown(self):
        mixins.datetime = datetime
        super(TestReadMixin, self).tearDown()

    def test_read_model_mixin_must_return_last_modified_header(self):
        dummy = DummyModel.objects.create(name='my dum dum')

        class DummyResource(ModelResource):
            model = DummyModel

        request = self.req.get('/dummies')
        mixin = ReadModelMixin()
        mixin.resource = DummyResource

        response = mixin.get(request, dummy.id)
        self.assertEquals(dummy.name, response.cleaned_content.name)
        self.assertTrue(response.headers.has_key('Last-Modified'))
        last_modified = response.headers['Last-Modified']
        # no error should occur, meaning we have the right format
        last_modified_datetime = parse_http_date(last_modified)
        self.assertEqual(last_modified_datetime, time.mktime(dummy.last_modified.timetuple()))

    def test_read_model_mixin_must_return_last_modified_header_as_now(self):
        dummier = DummierModel.objects.create(name='my dummier')

        class DummierResource(ModelResource):
            model = DummierModel

        request = self.req.get('/dummiers')
        mixin = ReadModelMixin()
        mixin.resource = DummierResource

        response = mixin.get(request, dummier.id)
        self.assertEquals(dummier.name, response.cleaned_content.name)
        self.assertTrue(response.headers.has_key('Last-Modified'))
        last_modified = response.headers['Last-Modified']
        # no error should occur, meaning we have the right format
        last_modified_datetime = parse_http_date(last_modified)
        self.assertEqual(last_modified_datetime, time.mktime(datetime(2012, 12, 12, 6, 6, 6).timetuple()))

class TestUpdateModelMixin(TestMixinsBase):

    def setUp(self):
        super(TestUpdateModelMixin, self).setUp()
        self.dummy = DummyModel.objects.create(name='dummy1')

        class DummyResource(ModelResource):
            model = DummyModel
        self.mixin = UpdateModelMixin()
        self.mixin.resource = DummyResource

    def test_update_model(self):
        """
        Making sure update still working fine
        """
        dummy = DummyModel.objects.get(id=1)

        update_data = {'name': 'updated_name'}
        request = self.req.put('/dummy/1', data=update_data)
        self.mixin.CONTENT = update_data

        response = self.mixin.put(request, id=dummy.id)

        self.assertEqual(dummy.name, 'dummy1')
        self.assertEqual(response.name, 'updated_name')
        self.assertEqual(response.id, dummy.id)

        #get dummy again now it should have the new name
        dummy = DummyModel.objects.get(id=dummy.id)
        self.assertEqual(dummy.name, response.name)

    def test_update_not_exist_model_return_404(self):
        """
        When make a put request to non-existing object in update mixin model, it should return 404
        """

        with self.assertRaises(DummyModel.DoesNotExist):
            DummyModel.objects.get(id=999)

        update_data = {'name': 'new_dummy'}
        request = self.req.put('/dummy/999', data=update_data)
        self.mixin.CONTENT = update_data

        self.assertRaises(ErrorResponse, self.mixin.put, request, id=999)

class TestUpdateOrCreateModelMixin(TestMixinsBase):

    def setUp(self):
        super(TestUpdateOrCreateModelMixin, self).setUp()
        self.dummy = DummyModel.objects.create(name='dummy1')

        class DummyResource(ModelResource):
            model = DummyModel
        self.mixin = UpdateOrCreateModelMixin()
        self.mixin.resource = DummyResource

    def test_update_model(self):
        """
        Making sure update still working fine
        """
        dummy = DummyModel.objects.get(id=1)

        update_data = {'name': 'updated_name'}
        request = self.req.put('/dummy/1', data=update_data)
        self.mixin.CONTENT = update_data

        response = self.mixin.put(request, id=dummy.id)

        self.assertEqual(dummy.name, 'dummy1')
        content = response.raw_content
        self.assertEqual(content.name, 'updated_name')
        self.assertEqual(content.id, dummy.id)

        #get dummy again now it should have the new name
        dummy = DummyModel.objects.get(id=dummy.id)
        self.assertEqual(dummy.name, content.name)

    def test_creation_on_put_not_exist_model(self):
        """
        When make a put request to non-existing object in update or create mixin model, it should create new object
        and return 201
        """

        with self.assertRaises(DummyModel.DoesNotExist):
            DummyModel.objects.get(id=999)

        self.assertEqual(DummyModel.objects.count(), 1)
        update_data = {'name': 'new_dummy'}
        request = self.req.put('/dummy/999', data=update_data)
        self.mixin.CONTENT = update_data

        response = self.mixin.put(request, id=999)

        self.assertEqual(response.status, 201)
        new_dummy = DummyModel.objects.get(id=999)
        self.assertEqual(new_dummy.name, 'new_dummy')
        self.assertEqual(DummyModel.objects.count(), 2)

class TestCreateModelMixin(TestMixinsBase):

    def setUp(self):
        super(TestCreateModelMixin, self).setUp()
        self.dummy = DummyModel.objects.create(name='dummy1')

        class DummyResource(ModelResource):
            model = DummyModel

            def url(self, instance):
                return '/dummy/%s' % instance.id
        self.mixin = CreateModelMixin()
        self.mixin.resource = DummyResource

    def test_post_to_create_must_return_content_location_header(self):

        with self.assertRaises(DummyModel.DoesNotExist):
            DummyModel.objects.get(name='new_dummy')

        self.assertEqual(DummyModel.objects.count(), 1)
        form_data = {'name': 'new_dummy'}
        request = self.req.post('/dummies', data=form_data)
        self.mixin.CONTENT = form_data

        response = self.mixin.post(request)
        self.assertEqual(DummyModel.objects.count(), 2)
        self.assertEqual(response.status, 201)
        self.assertEqual(response.cleaned_content.name, 'new_dummy')
        self.assertTrue(response.headers.has_key('Content-Location'))
        self.assertEqual(response.headers['Content-Location'], '/dummy/2')


class MockPaginatorView(PaginatorMixin, View):
    total = 60

    def get(self, request):
        return range(0, self.total)

class TestPaginatorMixin(TestCase):
    def setUp(self):
        self.req = RequestFactory()

    def _assert_links(self, links, rel, href):
        self.assertEqual(links[rel]['rel'], rel)
        self.assertEqual(links[rel]['href'], href)


    def _assert_page_info(self, content, expected_pages, expected_page, expected_total, expected_per_page):
        self.assertEqual(content['page'], expected_page)
        self.assertEqual(content['pages'], expected_pages)
        self.assertEqual(content['per_page'], expected_per_page)
        self.assertEqual(content['total'], expected_total)

    def test_paginator_mixin_return_nav_info_first_page(self):
        """
        Paginator mixin should return navigation links including
        self, first, last, next, previous when applicable
        also information of page, total pages, total number of objects, how many object per page
        - First page should not return  prev navigation link
        """
        request = self.req.get('/paginator')
        response = MockPaginatorView.as_view(limit=10)(request)
        content = json.loads(response.content)

        self._assert_page_info(content, 6, 1, 60, 10)
        self.assertTrue(content.has_key('links'))
        links = content['links']

        #assert self
        self.assertTrue(links.has_key('self'))
        self._assert_links(links, 'self', 'http://testserver/paginator')

        #assert next
        self.assertTrue(links.has_key('next'))
        self._assert_links(links, 'next', 'http://testserver/paginator?page=2')

        #assert no prev
        self.assertFalse(links.has_key('previous'))

        #assert first
        self.assertTrue(links.has_key('first'))
        self._assert_links(links, 'first','http://testserver/paginator')

        #assert last
        self.assertTrue(links.has_key('last'))
        self._assert_links(links, 'last', 'http://testserver/paginator?page=6')

    def test_paginator_mixin_return_nav_info_last_page(self):
        """
        Paginator mixin should return navigation links including
        self, first, last, next, previous when applicable
        - Last page should not have next navigation link
        """
        request = self.req.get('/paginator?page=3')
        response = MockPaginatorView.as_view(limit=20)(request)
        content = json.loads(response.content)

        self._assert_page_info(content, 3, 3, 60, 20)
        self.assertTrue(content.has_key('links'))
        links = content['links']

        #assert self
        self.assertTrue(links.has_key('self'))
        self._assert_links(links, 'self', 'http://testserver/paginator?page=3')

        #assert no next
        self.assertFalse(links.has_key('next'))

        #assert prev
        self.assertTrue(links.has_key('previous'))
        self._assert_links(links, 'previous', 'http://testserver/paginator?page=2')

        #assert first
        self.assertTrue(links.has_key('first'))
        self._assert_links(links, 'first','http://testserver/paginator')

        #assert last
        self.assertTrue(links.has_key('last'))
        self._assert_links(links, 'last', 'http://testserver/paginator?page=3')

    def test_paginator_mixin_return_nav_info_only_one_page(self):
        """
        Paginator mixin should return navigation links.
        If there's only one page, paginator should not return navigation links for prev and next
        """
        request = self.req.get('/paginator')
        response = MockPaginatorView.as_view(limit=60)(request)
        content = json.loads(response.content)

        self._assert_page_info(content, 1, 1, 60, 60)
        self.assertTrue(content.has_key('links'))
        links = content['links']

        #assert self
        self.assertTrue(links.has_key('self'))
        self._assert_links(links, 'self', 'http://testserver/paginator')

        #assert no next
        self.assertFalse(links.has_key('next'))

        #assert no prev
        self.assertFalse(links.has_key('previous'))

        #assert first
        self.assertTrue(links.has_key('first'))
        self._assert_links(links, 'first','http://testserver/paginator')

        #assert last
        self.assertTrue(links.has_key('last'))
        self._assert_links(links, 'last', 'http://testserver/paginator')

    def test_paginator_mixin_return_nav_info_with_limit(self):
        """
        Paginator mixin should return navigation links including
        self, first, last, next, previous when applicable
        - Links should include 'limit' parameter if different from default
        """
        request = self.req.get('/paginator?page=3&limit=10')
        response = MockPaginatorView.as_view(limit=20)(request)
        content = json.loads(response.content)

        self._assert_page_info(content, 6, 3, 60, 10)
        self.assertTrue(content.has_key('links'))
        links = content['links']

        #assert self
        self.assertTrue(links.has_key('self'))
        self._assert_links(links, 'self', 'http://testserver/paginator?page=3&limit=10')

        #assert no next
        self.assertTrue(links.has_key('next'))
        self._assert_links(links, 'next', 'http://testserver/paginator?page=4&limit=10')

        #assert prev
        self.assertTrue(links.has_key('previous'))
        self._assert_links(links, 'previous', 'http://testserver/paginator?page=2&limit=10')

        #assert first
        self.assertTrue(links.has_key('first'))
        self._assert_links(links, 'first','http://testserver/paginator?limit=10')

        #assert last
        self.assertTrue(links.has_key('last'))
        self._assert_links(links, 'last', 'http://testserver/paginator?page=6&limit=10')