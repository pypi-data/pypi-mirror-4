from restorm.resource import Resource

class Book(Resource):
    class Meta:
        list = r'^book/$'
        item = r'^book/(?P<id>\d)$'
