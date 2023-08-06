from django.contrib import admin

from .models import (
    Feed, FeedEntry, FeedEnclosure, FeedContent, KeywordFilter
)


class FeedAdmin(admin.ModelAdmin):
    filter_horizontal = ('filters', )
    search_fields = ('title', 'subtitle', 'description')
    list_display = ('title', 'url', 'updated', 'active', 'error_state')
    list_display_links = ('title', 'url')
    list_filter = ('updated', 'active', 'error_state')

    readonly_fields = (
        'updated', 'error_state', 'error_description', 'error_date'
    )


class FeedEnclosureInline(admin.StackedInline):
    model = FeedEnclosure
    extra = 0


class FeedContentInline(admin.StackedInline):
    model = FeedContent
    extra = 0


class FeedEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'published'
    list_display = ('published', 'title', 'author', 'feed')
    list_filter = ('feed', )
    search_fields = ('title', 'author', 'summary')

    readonly_fields = (
        'entry_id',
    )

    inlines = (FeedEnclosureInline, FeedContentInline)


class KeywordFilterAdmin(admin.ModelAdmin):
    pass


admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedEntry, FeedEntryAdmin)
admin.site.register(KeywordFilter, KeywordFilterAdmin)
