from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin

from .models import *


# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'thumbnail_tag')

    def thumbnail_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="%s"/>' % obj.image.thumbnail.url
            )
        return "-"

    thumbnail_tag.short_description = 'Thumbnail'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'country', 'slug')


class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'in_display', 'thumbnail_tag')

    def thumbnail_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="%s"/>' % obj.image.thumbnail.url
            )
        return "-"

    thumbnail_tag.short_description = 'Thumbnail'

    def save_model(self, request, obj, form, change):

        if obj.in_display:

            current_saved_default = ProfileImage.displayed.filter(profile=obj.profile, in_display=True)
            print('current', current_saved_default)
            if current_saved_default.exists():
                current_saved = current_saved_default[0]
                current_saved.in_display = False
                current_saved.save()
        obj.save()


admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileImage, ProfileImageAdmin)
admin.site.register(Comments, MPTTModelAdmin)
admin.site.register(Post, PostAdmin)
