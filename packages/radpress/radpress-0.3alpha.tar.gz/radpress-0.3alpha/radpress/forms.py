from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from radpress.models import Article, Page, Tag
from radpress.readers import RstReader


class PageForm(forms.ModelForm):
    class Meta:
        model = Page


class ZenModeForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('content', )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ZenModeForm, self).__init__(*args, **kwargs)

        if self.instance.pk is None:
            zen_mode_url = reverse('radpress-zen-mode')

        else:
            zen_mode_url = reverse(
                'radpress-zen-mode-update', args=[self.instance.pk])

        content_initial = [
            "Title here",
            "##########",
            ":slug: title-here",
            ":tags: world, big bang, sheldon",
            ":published: no",
            "",
            "Content here..."
        ]

        content = self.fields['content']
        content.widget = forms.Textarea(attrs={'class': 'zen-mode-textarea'})
        content.initial = '\n'.join(content_initial)
        content.help_text = _("You can also edit with "
                              "<a href='%s'>zen mode</a>.") % zen_mode_url

    def clean_content(self):
        field = self.cleaned_data.get('content')
        self.content_body, self.metadata = RstReader(field).read()

        slug = self.metadata.get('slug')

        if self.metadata.get('title') is None or slug is None:
            msg = _("Title or slug can not be empty.")
            raise forms.ValidationError(msg)

        if (self.instance.pk is None
                and Article.objects.filter(slug=slug).exists()):

            msg = _("Slug should be unique.")
            raise forms.ValidationError(msg)

        return field

    def save(self, **kwargs):
        title = self.metadata.get('title')
        slug = self.metadata.get('slug')
        content = self.cleaned_data.get('content')
        is_published = self.metadata.get('published')

        if self.instance.pk is None:
            article = Article.objects.create(
                author=self.user,
                title=title,
                slug=slug,
                content=content,
                content_body=self.content_body,
                is_published=is_published)

        else:
            article = self.instance
            article.title = title
            article.slug = slug
            article.content = content
            article.content_body = self.content_body
            article.is_published = is_published
            article.save()

            article.articletag_set.all().delete()

        for tag_name in self.metadata.get('tags'):
            tag = Tag.objects.get_or_create(name=tag_name)[0]
            article.articletag_set.create(tag=tag)

        return article

    def save_m2m(self):
        # TODO: this method added for fixing admin form error. But why we need
        # to this method, i don't know. Please find better way to solve this
        # problem.
        pass
