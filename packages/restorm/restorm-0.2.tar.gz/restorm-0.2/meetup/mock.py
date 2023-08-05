from restorm.clients.mockclient import BaseMockApiClient
from restorm.clients.jsonclient import JSONClientMixin, json

class MockLibraryClient(BaseMockApiClient, JSONClientMixin):
    pass

client = MockLibraryClient(
    responses={
        'book/1': {
            'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                {'id': 1, 'title': 'Dive into Python', 'author': 'http://localhost/api/author/1'}
            ))
        },
        'author/1': {
            'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                {'id': 1, 'name': 'Mark Pilgrim'}
            ))
        },
    },
    root_uri='http://localhost/api/'
)
