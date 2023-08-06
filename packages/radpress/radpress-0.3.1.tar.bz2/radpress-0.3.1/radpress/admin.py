from django.contrib import admin
from radpress.models import Article, EntryImage, Menu, Page, Tag
from radpress.forms import PageForm, ZenModeForm


class ZenModeAdminMixin(object):
    form = ZenModeForm

    class Media:
        css = {
            'all': ('radpress/css/zen_mode_admin.css',)
        }


class ArticleAdmin(ZenModeAdminMixin, admin.ModelAdmin):
    list_display = (
        'title', 'author', 'created_at', 'updated_at', 'tag_list',
        'is_published')
    list_filter = ('is_published', 'tags')
    list_editable = ('is_published',)

    def tag_list(self, obj):
        tag_list = [tag.name for tag in obj.tags.all()]

        return ', '.join(tag_list)

    def save_model(self, request, obj, form, change):
        # TODO: is it required?
        if not change:
            obj.author = request.user

        obj.save()

admin.site.register(Article, ArticleAdmin)


class PageAdmin(admin.ModelAdmin):
    form = PageForm

admin.site.register(Page, PageAdmin)


class TagAdmin(admin.ModelAdmin):
    def articles(self, obj):
        return obj.article_set.count()

    list_display = ['name', 'slug', 'articles']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Tag, TagAdmin)
admin.site.register(Menu, admin.ModelAdmin)


class EntryImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', '__unicode__', 'name')
    list_display_links = ('__unicode__',)
    search_fields = ('image', 'name')

admin.site.register(EntryImage, EntryImageAdmin)
