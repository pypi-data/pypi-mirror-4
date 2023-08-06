import os.path
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.test.client import Client
from radpress.models import Article, Page, Tag
from radpress.templatetags.radpress_tags import restructuredtext


class Test(TestCase):
    fixtures = [os.path.join(os.path.dirname(__file__), 'data.json')]

    def setUp(self):
        self.client = Client()

        # define article
        self.article1 = Article.objects.get(pk=1)

        # define user
        self.user1 = User.objects.get(username='gokmen')
        self.user1.set_password('secret')
        self.user1.save()

        # define second user password
        self.user2 = User.objects.get(username='defne')
        self.user2.set_password('secret')
        self.user2.save()

    def test_all_published_articles(self):
        # check published article count
        self.assertEqual(Article.objects.all_published().count(), 1)

        # check published page count
        self.assertEqual(Page.objects.all_published().count(), 2)

    def test_open_private_and_public_article_details(self):
        for article in Article.objects.all():
            status_code = 200 if article.is_published else 404
            response = self.client.get(
                reverse('radpress-article-detail', args=[article.slug]))

            self.assertEqual(response.status_code, status_code)

    def test_preview_page(self):
        # try to get response with GET method
        response = self.client.get(reverse('radpress-preview'))
        expected_status_code = 302  # because, login required
        self.assertEqual(response.status_code, expected_status_code)

        self.client.login(username='gokmen', password='secret')
        response = self.client.get(reverse('radpress-preview'))
        expected_status_code = 405  # because, view only allows `post` method
        self.assertEqual(response.status_code, expected_status_code)

    def test_slugs(self):
        for article in Article.objects.all():
            slug = slugify(article.slug)
            self.assertEqual(article.slug, slug)

    def test_contents(self):
        for article in Article.objects.all():
            content_body = restructuredtext(article.content)
            self.assertEqual(article.content_body, content_body)

    def test_tags(self):
        # checks tag count from fixture
        self.assertEqual(Tag.objects.count(), 2)

        # create new tag and check slug
        tag_name = 'how I met your mother'
        tag = Tag.objects.create(name=tag_name)
        self.assertEqual(tag.slug, slugify(tag_name))

        # add tag to a published article and check count of tags
        self.article1.articletag_set.create(tag=tag)
        self.assertEqual(self.article1.tags.count(), 1)

        # try to filter articles for tags
        articles = Article.objects.filter(tags__name=tag_name)
        self.assertEqual(articles.count(), 1)

    def test_access_not_published_article(self):
        """
        If user is not authenticated, user can not access not published
        articles and pages.
        """
        article = Article.objects.get(slug='i-have-a-dream')
        page = Page.objects.get(slug='page-3-not-published')

        def get_responses():
            response_article = self.client.get(
                reverse('radpress-article-detail', args=[article.slug]))
            response_page = self.client.get(
                reverse('radpress-page-detail', args=[page.slug]))

            return response_article, response_page

        # if user is not authenticated to site:
        response_article, response_page = get_responses()
        self.assertEqual(response_article.status_code, 404)
        self.assertEqual(response_page.status_code, 404)

        # if user is not superuser and not author of the entries:
        self.client.login(username=self.user2.username, password='secret')
        self.assertFalse(self.user2.is_superuser)
        response_article, response_page = get_responses()
        self.assertEqual(response_article.status_code, 404)
        self.assertEqual(response_page.status_code, 404)

        # if user is superuser but not the author of entries:
        self.user2.is_superuser = True
        self.user2.save()
        self.assertTrue(self.user2.is_superuser)
        response_article, response_page = get_responses()
        self.assertEqual(response_article.status_code, 200)
        self.assertEqual(response_page.status_code, 200)

        # if user is not superuser but the author of entries:
        article.author = self.user2
        article.save()

        self.user2.is_superuser = False
        self.user2.save()

        self.assertFalse(self.user2.is_superuser)
        response_article, response_page = get_responses()
        self.assertEqual(response_article.status_code, 200)
        self.assertEqual(response_page.status_code, 404)
