from django import forms
from django.forms import ModelForm

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
        exclude = ('identifier', 'url', 'template_override',)


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        #exclude = ('identifier', 'url', 'template_override',)
