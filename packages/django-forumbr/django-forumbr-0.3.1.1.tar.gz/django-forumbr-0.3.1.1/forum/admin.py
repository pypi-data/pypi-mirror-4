# -*- coding:utf-8 -*-

from django.contrib import admin

from .forms import ProfileAdminForm
from .models import Category, Forum, Thread, Reply, Profile

class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm


class ForumInlineModel(admin.StackedInline):
    model = Forum
    exclude = ('parent',)
    extra = 3
    max_num = 6


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}
    inlines = [ForumInlineModel]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum)
admin.site.register(Thread)
admin.site.register(Reply)
admin.site.register(Profile, ProfileAdmin)