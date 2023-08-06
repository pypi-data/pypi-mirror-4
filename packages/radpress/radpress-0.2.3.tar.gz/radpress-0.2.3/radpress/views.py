from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.views.generic import (
    DetailView, ListView, TemplateView, ArchiveIndexView)
from radpress.models import Article, Page, Tag
from radpress.settings import DATA


class TagMixin(object):
    def get_context_data(self, **kwargs):
        tags = Tag.objects.annotate(Count('article')).filter(
            article__count__gt=0, article__is_published=True)
        data = super(TagMixin, self).get_context_data(**kwargs)
        data.update({
            'tag_list': tags.values('name', 'slug')
        })

        return data


class Index(TagMixin, ListView):
    template_name = 'radpress/index.html'
    model = Article

    def get_queryset(self):
        return self.model.objects.all_published()[:DATA.get('RADPRESS_LIMIT')]

    def get_context_data(self, **kwargs):
        data = super(Index, self).get_context_data(**kwargs)
        data.update({'by_more': True})

        return data


class Detail(TagMixin, DetailView):
    template_name = 'radpress/detail.html'
    model = Article

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            self.model, slug=self.kwargs.get('slug'), is_published=True)

        return obj

    def get_context_data(self, **kwargs):
        data = super(Detail, self).get_context_data(**kwargs)
        data.update({
            'object_list': self.model.objects.all_published().values(
                'slug', 'title', 'updated_at')[:DATA.get('RADPRESS_LIMIT')]
        })

        return data


class PageDetail(Detail):
    template_name = 'radpress/page_detail.html'
    model = Page


class Archive(TagMixin, ArchiveIndexView):
    template_name = 'radpress/archive.html'
    model = Article
    date_field = 'created_at'
    paginate_by = 25

    def get_queryset(self):
        queryset = self.model.objects.all_published()

        # filter for tags, if possible...
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        return queryset.values('slug', 'title', 'updated_at')

    def get_context_data(self, **kwargs):
        data = super(Archive, self).get_context_data(**kwargs)
        data.update({
            'enabled_tag': self.request.GET.get('tag')
        })

        return data


class Preview(TemplateView):
    template_name = 'radpress/preview.html'
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        data = super(Preview, self).get_context_data(**kwargs)
        data.update({
            'content': self.request.POST.get('data', '')
        })

        return data

    def post(self, request, *args, **kwargs):
        return super(Preview, self).get(request, *args, **kwargs)


class Search(TemplateView):
    template_name = 'radpress/search.html'
    models = (Article, Page)

    def get_queryset(self):
        queryset = []
        q = self.request.GET.get('q')

        if not q:
            return queryset

        for model in self.models:
            queryset += model.objects.filter(
                Q(title__icontains=q) | Q(slug__icontains=q) |
                Q(content__icontains=q), is_published=True)

        return queryset

    def get_context_data(self, **kwargs):
        data = super(Search, self).get_context_data(**kwargs)
        data.update({'object_list': self.get_queryset()})

        return data
