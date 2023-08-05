import os

from unittest2 import TestCase

from restorm.clients.tests import LibraryApiClient
from restorm.clients.mockclient import MockClient, StringResponse, FileResponse, MockResponse, BaseMockApiClient
from restorm.clients.jsonclient import JSONClientMixin
from restorm.resource import Resource


class MockClientTests(TestCase):
    
    def test_request_mock_response(self):
        obj = {}
        
        predefined_response = MockResponse(
            {'Foo': 'Bar', 'Status': 200},
            obj
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertEqual(response.content, obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)

    def test_request_string_response(self):
        predefined_response = StringResponse(
            {'Foo': 'Bar', 'Status': 200},
            {}
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertEqual(response.content, '{}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)

    def test_file_response_with_unknown_file(self):
        non_existent_file = '__does_not_exist__.tmp'
        self.assertFalse(os.path.isfile(non_existent_file))
        self.assertRaises(ValueError, FileResponse, {}, non_existent_file)

    def test_request_file_response(self):
        predefined_response = FileResponse(
            {'Foo': 'Bar', 'Content-Type': 'text/python', 'Status': 200},
            '%s' % __file__
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertTrue(self.__class__.__name__ in response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/python')
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)



class MockApiClientTests(TestCase):
    def setUp(self):
        self.client = LibraryApiClient()
        
    def test_get(self):
        response = self.client.get('book/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.client.responses['book/']['GET'][1])
        
    def test_post(self):
        response = self.client.post('search/', {'q': 'Python'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Cache'], self.client.responses['search/']['POST'][0]['X-Cache'])
        self.assertEqual(response.content, self.client.responses['search/']['POST'][1])

    def test_page_not_found(self):
        uri = 'book/2'
        self.assertTrue(uri not in self.client.responses)

        response = self.client.get(uri)

        self.assertEqual(response.status_code, 404)

    def test_method_not_allowed(self):
        response = self.client.post('author/1', {})

        self.assertEqual(response.status_code, 405)
        
    def test_related(self):
        
        class Book(Resource):
            class Meta:
                list = r'^book/$'
                item = r'^book/(?P<isbn>\d)$'
                
        class Author(Resource):
            class Meta:
                list = (r'^author/$', 'author_set')
                item = r'^author/(?P<id>\d)$'

        book = Book.objects.get(isbn='978-1441413024', client=self.client)
        self.assertEqual(book.data['title'], self.client.responses['book/978-1441413024']['GET'][1]['title'])
        self.assertEqual(book.data['author'], self.client.responses['book/978-1441413024']['GET'][1]['author'])
        
        author = book.data.author
        self.assertEqual(author.data['name'], self.client.responses['author/1']['GET'][1]['name'])
        

class JSONMockApiClientTests(TestCase):
    """
    Tests whether you can easily use JSONClientMixin and BaseMockApiClient to
    create a new mock client using JSON responses.
    
    This is used as an example in the README.rst
    """
    
    def setUp(self):
        self.responses = {
            'book/1': {'GET': ({'Status': 200, 'Content-Type': 'application/json'}, 
                '{"id": 1, "name": "Dive into Python", "author": "http://www.example.com/api/author/1"}')}
        }

        class JSONMockApiClient(BaseMockApiClient, JSONClientMixin):
            pass

        self.client = JSONMockApiClient(responses=self.responses, root_uri='http://www.example.com/api/')

    def test_get_json(self):
        response = self.client.get('book/1')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Content-Type' in response)
        self.assertEqual(response['Content-Type'], 'application/json')

        self.assertEqual(response.content['name'], 'Dive into Python')
        self.assertEqual(response.content['author'], 'http://www.example.com/api/author/1')
