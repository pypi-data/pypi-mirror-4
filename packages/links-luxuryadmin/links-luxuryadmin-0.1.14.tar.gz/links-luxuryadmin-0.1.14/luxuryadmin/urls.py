from django.conf.urls import patterns, include, url
from models import PLUGINS

urls = ['luxuryadmin.views',
    # Collection
    url(r'^collection/$', 'collection',
        name="collection"),
    url(r'^collection/product/$', 'product',
        name="product"),
    url(r'^collection/product/(?P<product>[0-9]+)/$', 'product',
        name="product"),
    url(r'^xhr/products/$', 'xhr_products', name='xhr_products'),
    url(r'^xhr/product/(?P<pk>[0-9]*)/save/$', 'xhr_save_product',
        name="xhr_save_product"),
    url(r'^xhr/product/(?P<pk>[0-9]*)/save/(?P<type>[a-z]+)/$',
        'xhr_save_product', name="xhr_save_product"),
    url(r'^xhr/product/create/$', 'xhr_save_product', name="xhr_save_product"),
    url(r'^xhr/product/delete/(?P<product>[0-9]+)/$',
        'xhr_delete_product', name="xhr_delete_product"),
    
    url(r'^xhr/upload/photo/$', 'xhr_upload_photo', name="xhr_upload_photo"),
    url(r'^xhr/update_photos/$', 'xhr_update_photos',
        name="xhr_update_photos"),
    # Categories
    url(r'^categories/$', 'categories', name="categories"),
    url(r'^categories/new/$', 'category', name="category"),
    url(r'^categories/(?P<category>[0-9]+)/$', 'category', name="category"),
    url(r'^xhr/categories/$', 'xhr_categories', name='xhr_categories'),
    url(r'^xhr/category/delete/(?P<category>[0-9]+)/$',
        'xhr_delete_category', name="xhr_delete_category"),
    # Pages
    url(r'^pages/$', 'pages', name="pages"),
    url(r'^pages/new/$', 'page', name="page"),
    url(r'^pages/(?P<page>[0-9]+)/$', 'page', name="page"),
    url(r'^xhr/pages/$', 'xhr_pages', name='xhr_pages'),
    url(r'^xhr/paget/delete/(?P<page>[0-9]+)/$',
        'xhr_delete_page', name="xhr_delete_page"),
    url(r'^xhr/login/$', 'xhr_log_in', name="xhr_log_in"),
    url(r'^log_out/$', 'log_out', name="log_out"),
]

for plugin in PLUGINS:
    urls.append(url(r'^{}/'.format(plugin.name), include(
        '{}.urls'.format(plugin.app),
        namespace=plugin.name
    )))

urlpatterns = patterns(*urls)