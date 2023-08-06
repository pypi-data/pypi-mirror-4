from django.conf.urls import patterns, url
from radpress.views import (
    ArticleArchiveView, ArticleDetailView, ArticleListView, PreviewView,
    PageDetailView, SearchView, ZenModeView, ZenModeUpdateView)
from radpress.feeds import ArticleFeed

urlpatterns = patterns(
    '',

    url(r'^$',
        view=ArticleListView.as_view(),
        name='radpress-article-list'),

    url(r'^archives/$',
        view=ArticleArchiveView.as_view(),
        name='radpress-article-archive'),

    url(r'^detail/(?P<slug>[-\w]+)/$',
        view=ArticleDetailView.as_view(),
        name='radpress-article-detail'),

    url(r'^p/(?P<slug>[-\w]+)/$',
        view=PageDetailView.as_view(),
        name='radpress-page-detail'),

    url(r'^preview/$',
        view=PreviewView.as_view(),
        name='radpress-preview'),

    url(r'^search/$',
        view=SearchView.as_view(),
        name='radpress-search'),

    url(r'^zen/$',
        view=ZenModeView.as_view(),
        name='radpress-zen-mode'),

    url(r'zen/(?P<pk>\d+)/$',
        view=ZenModeUpdateView.as_view(),
        name='radpress-zen-mode-update'),

    url(r'^rss/$',
        view=ArticleFeed(),
        name='radpress-rss'),

    url(r'^rss/(?P<tags>[-/\w]+)/$',
        view=ArticleFeed(),
        name='radpress-rss')
)
