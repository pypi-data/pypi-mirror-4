from unittest2 import TestCase

from restorm.clients.tests import LibraryApiClient
from restorm.resource import ResourceManager, ResourceOptions, Resource


class ResourceTests(TestCase):
    
    def setUp(self):
        self.client = LibraryApiClient()
    
    def test_meta_class(self):

        class Book(Resource):
            class Meta:
                item = r'^book/(?P<isbn>\d)$'

        class Author(Resource):
            class Meta:
                list = (r'^author/$', 'author_set')
                item = r'^author/(?P<id>\d)$'
                root = 'http://someotherdomain/api/'
                
        class Store(Resource):
            pass

        self.assertTrue(hasattr(Book, '_meta'))
        self.assertTrue(isinstance(Book._meta, ResourceOptions))
        self.assertEqual(Book._meta.list, '')
        self.assertEqual(Book._meta.item, r'^book/(?P<isbn>\d)$')
        self.assertEqual(Book._meta.root, '')

        self.assertTrue(hasattr(Author, '_meta'))
        self.assertTrue(isinstance(Author._meta, ResourceOptions))
        self.assertEqual(Author._meta.list, (r'^author/$', 'author_set'))
        self.assertEqual(Author._meta.item, r'^author/(?P<id>\d)$')
        self.assertEqual(Author._meta.root, 'http://someotherdomain/api/')
        
        self.assertTrue(hasattr(Store, '_meta'))
        self.assertTrue(isinstance(Store._meta, ResourceOptions))
        self.assertEqual(Store._meta.list, '')
        self.assertEqual(Store._meta.item, '')
        self.assertEqual(Store._meta.root, '')

        self.assertNotEqual(Author._meta, Store._meta)
        self.assertNotEqual(Book._meta, Author._meta)
        self.assertNotEqual(Book._meta, Store._meta)
        
    def test_default_manager(self):
        """
        By default, there should be a default manager on RestObject.
        """

        class Book(Resource):
            pass

        class Author(Resource):
            pass
                
        self.assertTrue(isinstance(Book.objects, ResourceManager))
        self.assertTrue(Book.objects.object_class, Book)

        self.assertTrue(isinstance(Author.objects, ResourceManager))
        self.assertTrue(Author.objects.object_class, Author)

        self.assertNotEqual(Book.objects, Author.objects)
        
        book = Book()
        # Cannot test AttributeError with self.assertRaises
        try:
            book.objects.all()
        except AttributeError, e:
            self.assertEqual('%s' % e, 'Manager is not accessible via Book instances')
        
    def test_custom_manager(self):
        """
        Custom managers can be added on a RestObject.
        """
        
        class BookManager(ResourceManager):
            def filter_on_author(self, author_resource):
                return self.all(query=[('author', author_resource),])

        class Book(Resource):
            objects = BookManager()
            class Meta:
                list = r'^book/$'

        class Author(Resource):
            pass

        self.assertTrue(isinstance(Book.objects, BookManager))
        self.assertTrue(hasattr(Book.objects, 'filter_on_author'))
        self.assertTrue(Book.objects.object_class, Book)

        self.assertTrue(isinstance(Author.objects, ResourceManager))
        self.assertTrue(Author.objects.object_class, Author)

        self.assertNotEqual(Book.objects, Author.objects)

        book = Book()
        # Cannot test AttributeError with self.assertRaises
        try:
            book.objects
        except AttributeError, e:
            self.assertEqual('%s' % e, 'Manager is not accessible via Book instances')
        
    def test_custom_functions_and_attributes(self):
        """
        Alot of fiddling with class attributes, functions, meta classes, etc.
        is done to build a proper instance and/or class.
        
        This test validates some basic Python stuff to actually work as
        expected.
        """
        class Book(Resource):
            some_class_attribute = 'foobar'
            
            def __init__(self, *args, **kwargs):
                self.some_instance_attribute_before_init = 'foobar'
                super(Book, self).__init__(*args, **kwargs)
                self.some_instance_attribute_after_init = 'foobar'
            
            def get_title(self):
                return self.data['title'].title()
            
            class Meta:
                list = r'^book/$'
                item = r'^book/(?P<isbn>\d)$'
        
        self.assertTrue(hasattr(Book, 'get_title'))
        self.assertFalse(hasattr(Resource, 'get_title'))

        self.assertTrue(hasattr(Book, 'some_class_attribute'))
        self.assertEqual(Book.some_class_attribute, 'foobar')
        self.assertFalse(hasattr(Book, 'some_instance_attribute_before_init'))
        self.assertFalse(hasattr(Book, 'some_instance_attribute_after_init'))
        
        book = Book.objects.get(client=self.client, isbn='978-1441413024')
        self.assertEqual(book.data['title'], 'Dive into Python')
        self.assertTrue(hasattr(book, 'get_title'))
        self.assertEqual(book.get_title(), book.data['title'].title())

        self.assertTrue(hasattr(book, 'some_class_attribute'))
        self.assertEqual(book.some_class_attribute, 'foobar')
        self.assertTrue(hasattr(book, 'some_instance_attribute_before_init'))
        self.assertEqual(book.some_instance_attribute_before_init, 'foobar')
        self.assertTrue(hasattr(book, 'some_instance_attribute_after_init'))
        self.assertEqual(book.some_instance_attribute_after_init, 'foobar')
    
    def test_related_resources(self):
        class Book(Resource):
            class Meta:
                list = r'^book/$'
                item = r'^book/(?P<isbn>\d)$'

        book = Book.objects.get(client=self.client, isbn='978-1441413024')
        self.assertEqual(book.data['title'], 'Dive into Python')

        author_url = book.data['author']
        author = book.data.author

        self.assertTrue(isinstance(author, Resource))
        self.assertEqual(author_url, author.absolute_url)
        self.assertEqual(author.data['name'], 'Mark Pilgrim')
