from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.test import TestCase
from radpress.models import Article
from radpress.templatetags.radpress_tags import restructuredtext


class Tests(TestCase):
    """
    Radpress tests.
    """

    def setUp(self):
        """
        Simple data for testing Radpress.
        """
        self.author = User.objects.create(username='radpress')
        self.article = Article.objects.create(
            author=self.author,
            title="Welcome to Radpress!",
            content="This entry is created for testing.",
            is_published=True)
        self.article_not_published = Article.objects.create(
            author=self.author,
            title="I Have A Dream...")

    def test_all_published_articles(self):
        self.assertEqual(Article.objects.all_published().count(), 1)

    def test_slugs(self):
        for article in Article.objects.all():
            slug = slugify(article.slug)
            self.assertEqual(article.slug, slug)

    def test_contents(self):
        for article in Article.objects.all():
            content_body = restructuredtext(article.content)
            self.assertEqual(article.content_body, content_body)
