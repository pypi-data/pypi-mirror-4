import httplib2

client = httplib2.Http()

import json

headers, content = client.request('http://library/api/book/1', method='GET')
book_data = json.loads(content)
# >>> book_data
# {
#     'title': 'Dive into Python',
#     'author': 'http://library/api/author/1'
# }

headers, content = client.request(book_data['author'], method='GET')
author_data = json.loads(content)
# >>> author_data
# {
#     'name': 'Mark Pilgrim'
# }

print book_data['title'] # Dive into Python
print author_data['name'] # Mark Pilgrim
