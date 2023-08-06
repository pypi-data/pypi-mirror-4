from django.utils import unittest

from test_app.models import Author, Book, FeaturedAuthor


class StatusableModelTestCase(unittest.TestCase):

    def setUp(self):

        # Create some test authors

        self.author1 = Author.objects.create(first_name='Dave', last_name='Eggers')
        self.author2 = Author.objects.create(first_name='George', last_name='Martin')
        self.author3 = Author.objects.create(first_name='Noam', last_name='Chomsky')

        # Create some test books

        self.book1 = Book.objects.create(name='A Heartbreaking Work of Staggering Genius', author=self.author1)
        self.book2 = Book.objects.create(name='You Shall Know Our Velocity', author=self.author1)
        self.book3 = Book.objects.create(name='A Game of Thrones', author=self.author2)
        self.book4 = Book.objects.create(name='Manufacturing Consent: The Political Economy of the Mass Media', author=self.author3)

        # Create some test featured authors

        self.featured1 = FeaturedAuthor.objects.create(author=self.author1)
        self.featured2 = FeaturedAuthor.objects.create(author=self.author2)
        self.featured3 = FeaturedAuthor.objects.create(author=self.author3)

    def tearDown(self):
        
        self.author1.delete()
        self.author2.delete()
        self.author3.delete()

        self.book1.delete()
        self.book2.delete()
        self.book3.delete()
        self.book4.delete()

        self.featured1.delete()
        self.featured2.delete()
        self.featured3.delete()

    def test_inactive(self):

        Author.objects.deactivate()

        # Test queryset methods

        active_authors = Author.objects.active()
        inactive_authors = Author.objects.inactive()

        self.assertEqual(active_authors.count(), 0)
        self.assertEqual(inactive_authors.count(), 3)

        # Test properties

        for author in inactive_authors:
            self.assertFalse(author.is_active)
            self.assertTrue(author.is_inactive)

    def test_active(self):

        Author.objects.activate()

        # Test queryset methods

        active_authors = Author.objects.active()
        inactive_authors = Author.objects.inactive()

        self.assertEqual(active_authors.count(), 3)
        self.assertEqual(inactive_authors.count(), 0)

        # Test properties

        for author in active_authors:
            self.assertTrue(author.is_active)
            self.assertFalse(author.is_inactive)

    def test_instance(self):

        # Test instance methods

        self.author1.activate()
        self.assertTrue(self.author1.is_active)
        self.assertFalse(self.author1.is_inactive)

        self.author1.deactivate(save=False)
        self.assertTrue(self.author1.is_inactive)
        self.assertFalse(self.author1.is_active)

        author1 = Author.objects.get(pk=self.author1.pk)
        self.assertTrue(author1.is_active)
        self.assertFalse(author1.is_inactive)

    def test_single_active(self):

        # Simple activation
        
        self.featured1.activate()
        self.assertTrue(self.featured1.is_active)
        self.assertFalse(self.featured1.is_inactive)
        self.assertIsInstance(FeaturedAuthor.objects.active(), FeaturedAuthor)

        # Activate another record

        self.featured2.activate()

        self.featured1 = FeaturedAuthor.objects.get(pk=self.featured1.pk) # Reload from DB

        self.assertFalse(self.featured1.is_active)
        self.assertTrue(self.featured1.is_inactive)
        self.assertTrue(self.featured2.is_active)
        self.assertFalse(self.featured2.is_inactive)
        self.assertIsInstance(FeaturedAuthor.objects.active(), FeaturedAuthor)

        # Test activating a group

        featured = FeaturedAuthor.objects.all()
        active = featured[0]
        featured = featured.activate()

        i = 0

        featured_updated = FeaturedAuthor.objects.all()

        for feature in featured_updated:
            if (feature.pk == active.pk):
                self.assertTrue(feature.is_active)
            else:
                self.assertFalse(feature.is_active)
            i += 1

        self.assertIsInstance(FeaturedAuthor.objects.active(), FeaturedAuthor)

