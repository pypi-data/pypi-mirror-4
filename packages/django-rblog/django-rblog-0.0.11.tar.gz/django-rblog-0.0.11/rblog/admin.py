# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms

class PostAdminForm(admin.ModelAdmin):

    list_display = ('title', 'user', 'creation_date')
    list_filter = ('user', 'creation_date')
    ordering = ('-creation_date',)
    search_fields = ('title','text',)

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

    # http://www.userlinux.net/django-datos-del-usuario.html
    exclude = ('user',)

    # http://www.b-list.org/weblog/2008/dec/24/admin/
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )

admin.site.register(mymodels.Post, PostAdminForm)
admin.site.register(mymodels.Comments)
