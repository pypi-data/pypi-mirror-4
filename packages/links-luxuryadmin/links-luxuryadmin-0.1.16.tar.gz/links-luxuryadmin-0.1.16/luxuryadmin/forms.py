from django import forms
from django.forms import ModelForm
from tinymce.widgets import TinyMCE
from suave.models import Page
from collection.models import Product, Category


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label=u'Username')
    password = forms.CharField(widget=forms.PasswordInput, label=u'Password')


class ProductForm(ModelForm):
    class Meta:
        model = Product
        exclude = ('in_date', 'num_views', 'slug')


class ProductTableRow(ModelForm):
    class Meta:
        model = Product
        fields = ('featured', 'sold', 'category', 'live')


class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = (
            'title',
            'status',
            'slug',
            'body',
            'parent',
            'header_image',
        )
        widgets = {
            'body': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
            'sort_index',
            'slug',
            'is_special',
            'introduction_text',
            'image'
        )
        #exclude = ('identifier', 'url', 'template_override',)
