from django.contrib import admin
from django.forms import ModelForm
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter

from .models import (
    Category,
    Post, Translations
)


class NameStartsWithFilter(admin.SimpleListFilter):
    title = "Name starts with"
    parameter_name = 'name__startswith'

    def lookups(self, request, model_admin):
        names = Category.objects.values_list('name', flat=True).distinct()
        return [(name[0].upper(), name[0].lower()) for name in names]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(slug__istartswith=self.value().lower())
        return queryset


class CategoryAdminForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__" # for Django 1.8+


    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['main_post'].queryset = Post.objects.filter(category__id=self.instance.id)
            self.fields['main_post2'].queryset = Post.objects.filter(category__id=self.instance.id)
            self.fields['main_post3'].queryset = Post.objects.filter(category__id=self.instance.id)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_post', 'main_post2', 'main_post3')
    search_fields = ['slug']
    
    list_filter = (NameStartsWithFilter,)

    form = CategoryAdminForm

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(CategoryAdmin, self).get_form(request, obj, **kwargs)
    
    def custom_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

    custom_delete_selected.short_description = 'Удалить выбранные категории'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category_name', 'create_at',
                    'update_at', 'published', 'changed_by_manager', 'position_in_category')
    search_fields = ['id', 'name', 'category__name']
    list_filter = [('category', RelatedOnlyDropdownFilter), 'published']

    actions = ['delete_selected', 'publish_selected', 'unpublish_selected']

    exclude = ("changed_by_manager",)

    def group_manager_exist(self, request):
        try:
            return request.user.groups.filter(name="Manager").exists()
        except:
            return False

    def get_form(self, request, obj=None, **kwargs):
        if self.group_manager_exist(request):
            self.exclude = ("published", "changed_by_manager")
        else:
            self.exclude = [x for x in self.exclude if x == "changed_by_manager"]
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        return form

    def category_name(self, obj):
        return obj.category.name

    def publish_selected(self, request, queryset):
            queryset.update(published=True)

    def unpublish_selected(self, request, queryset):
        queryset.update(published=False)

    def get_actions(self, request):
        actions = super(PostAdmin, self).get_actions(request)
        if self.group_manager_exist(request):
            try:
                del actions['publish_selected']
                del actions['unpublish_selected']
                del actions['delete_selected']
                return actions
            except:
                return actions
        return actions


    def save_model(self, request, obj, form, change):
        if change and request.user.groups.filter(name='Manager').exists():
            obj.changed_by_manager = True
        return super().save_model(request, obj, form, change)

    def delete_selected(self, request, queryset):
        queryset.delete()

    publish_selected.short_description = "Опубликовать выбранные посты"
    unpublish_selected.short_description = "Снять с публикации выбранные посты"
    delete_selected.short_description = 'Удалить выбранные посты'
    category_name.short_description = 'Категория'

@admin.register(Translations)
class TranslationsAdmin(admin.ModelAdmin):
    list_display = ('content_uz', 'content_en')