# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from facebook_api.admin import FacebookModelAdmin
from facebook_posts.models import PostOwner, Comment
from models import User

class PostInline(generic.GenericTabularInline):
    model = PostOwner
    ct_field = 'owner_content_type'
    ct_fk_field = 'owner_id'
    fields = ('post',)
    readonly_fields = fields
    extra = False
    can_delete = False

class CommentInline(generic.GenericTabularInline):
    model = Comment
    ct_field = 'author_content_type'
    ct_fk_field = 'author_id'
    fields = ('message','likes_count')
    readonly_fields = fields
    extra = False
    can_delete = False

class UserAdmin(FacebookModelAdmin):
    list_display = ('name','first_name','last_name','gender')
    list_display_links = ('name',)
    list_filter = ('gender',)
    search_fields = ('name',)
    inlines = [PostInline, CommentInline]

#    def get_readonly_fields(self, *args, **kwargs):
#        fields = super(UserAdmin, self).get_readonly_fields(*args, **kwargs)
#        return fields + ['likes']

admin.site.register(User, UserAdmin)