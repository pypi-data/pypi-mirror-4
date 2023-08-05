from django.contrib import admin

from sources.models import Source, Language, LanguageExtension

admin.site.register(Source)

class LanguageExtensionInline(admin.TabularInline):
    model = LanguageExtension
    extra = 1

class LanguageAdmin(admin.ModelAdmin):
    inlines = [LanguageExtensionInline, ]

admin.site.register(Language, LanguageAdmin)
