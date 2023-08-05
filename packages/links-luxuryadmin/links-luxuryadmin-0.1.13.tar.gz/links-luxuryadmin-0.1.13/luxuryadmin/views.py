import datetime
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.core.files.images import ImageFile

import simplejson as json

from sorl.thumbnail import get_thumbnail
from suave.models import Page
from collection.models import Product, Photo, Category

from .forms import (LoginForm, ProductForm, ProductTableRow, PageForm,
    CategoryForm)
from .utils import random_filename, qsearch


@user_passes_test(lambda u: u.is_staff)
def collection(request):
    context = {
        'form_new_product': ProductForm,
    }
    # Legacy code for follit
    if settings.LUX_GROUP_BY_CATEGORY:
        context['table_rows'] = []
        for category in Category.objects.all():
            products = category.products.all()
            if products.count() < 1:
                continue
            context['table_rows'].append(dict(
                category=category,
                products=[{
                    'row': ProductTableRow(instance=product),
                    'form': ProductForm(instance=product)
                } for product in products]
            ))
    else:
        context['products'] = [{
            'row': ProductTableRow(instance=product),
            'form': ProductForm(instance=product)
        } for product in Product.objects.all()]
    return TemplateResponse(request, 'luxuryadmin/collection.html', context)


"""
Categories
"""
@user_passes_test(lambda u: u.is_staff)
def categories(request):
    return TemplateResponse(request, 'luxuryadmin/categories.html')


@user_passes_test(lambda u: u.is_staff)
def category(request, category=None):
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    if category:
        category = get_object_or_404(Category, id=category)
        form = CategoryForm(data, instance=category)
    else:
        form = CategoryForm(data)

    if form.is_valid():
        if category:
            form.save()
        else:
            category = form.save(commit=False)
            if not category.slug:
                category.slug = slugify(category.name)

            category.save()
            return HttpResponseRedirect(
                reverse('luxuryadmin:category', kwargs={
                    'category': category.id
                })
            )

    return TemplateResponse(request, 'luxuryadmin/category.html', dict(
        form=form,
        category=category,
    ))


@user_passes_test(lambda u: u.is_staff)
def xhr_categories(request):
    search_string = request.GET.get('q', '')
    # order_by = request.GET.get('order_by', None)
    # order = request.GET.get('order', None)
    output = []
    qs = Category.objects
    if len(search_string) > 0:
        qs = qs.filter(name__icontains=search_string)
    for category in qs.all():
        category_row = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'url': {
                'edit': reverse('luxuryadmin:category', kwargs={
                    'category': category.id
                }),
                'view': category.url,
                'delete': reverse('luxuryadmin:xhr_delete_category', kwargs={
                    'category': category.id
                })
            }
        }
        output.append(category_row)

    return HttpResponse(json.dumps(output), content_type='application/json')


def xhr_delete_category(request, category):
    category = get_object_or_404(Category, pk=category)
    category.delete()
    return HttpResponse("OK")


"""
Pages
"""
@user_passes_test(lambda u: u.is_staff)
def pages(request):
    return TemplateResponse(request, 'luxuryadmin/pages.html')


@user_passes_test(lambda u: u.is_staff)
def page(request, page=None):
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    if page:
        page = get_object_or_404(Page, id=page)
        form = PageForm(data, instance=page)
    else:
        form = PageForm(data)

    if form.is_valid():
        if page:
            form.save()
        else:
            page = form.save(commit=False)
            if not page.slug:
                page.slug = slugify(page.name)

            page.save()
            return HttpResponseRedirect(
                reverse('luxuryadmin:page', kwargs={
                    'page': page.id
                })
            )

    return TemplateResponse(request, 'luxuryadmin/page.html', dict(
        form=form,
        page=page,
    ))


@user_passes_test(lambda u: u.is_staff)
def xhr_pages(request):
    search_string = request.GET.get('q', '')
    # order_by = request.GET.get('order_by', None)
    # order = request.GET.get('order', None)
    output = []
    qs = Page.objects
    if len(search_string) > 0:
        qs = qs.filter(title__icontains=search_string)
    for page in qs.all():
        page_row = {
            'id': page.id,
            'title': page.title,
            'status': page.status.title(),
            'url': {
                'view': page.url,
                'edit': reverse('luxuryadmin:page', kwargs={
                    'page': page.id
                }),
                'delete': reverse('luxuryadmin:xhr_delete_page', kwargs={
                    'page': page.id
                })
            },
        }
        output.append(page_row)

    return HttpResponse(json.dumps(output), content_type='application/json')


def xhr_delete_page(request, page):
    page = get_object_or_404(Page, pk=page)
    page.delete()
    return HttpResponse("OK")

"""
Products
"""
@user_passes_test(lambda u: u.is_staff)
def product(request, product=None):
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    if product:
        product = get_object_or_404(Product, id=product)
        form = ProductForm(data, instance=product)
    else:
        form = ProductForm(data)

    if form.is_valid():
        if product:
            form.save()
        else:
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)
            product.save()

        uploads = request.POST.getlist('photos', [])
        i = 1
        photos = []
        for image in uploads:
            photo, created = Photo.objects.get_or_create(
                image=image,
                product=product,
                defaults={
                    'sort_index': i
                }
            )
            photo.sort_index = i
            if image == request.POST.get('image', False):
                photo.sort_index = 0
            else:
                i += 1
            photos.append(photo)
            photo.save()

        for old_photo in product.photos.all():
            if old_photo not in photos:
                old_photo.delete()

        limit = 5
        i = 0
        for photo in product.photos.all():
            if i >= limit:
                photo.delete()
            i += 1
        return HttpResponseRedirect(
            reverse('luxuryadmin:product', kwargs={
                'product': product.id,
            })
        )

    today = datetime.date.today().strftime('%d/%m/%Y')
    return TemplateResponse(request, 'luxuryadmin/product.html', dict(
        form_new_product=form,
        product=product,
        today=today,
    ))


@user_passes_test(lambda u: u.is_staff)
def xhr_upload_photo(request):
    """Upload photos from form, return filenames and urls and thumbnails."""
    def handle_uploaded_image(orig_filename, f):
        folder = settings.MEDIA_PATH['product']
        f = ImageFile(f)
        fs = FileSystemStorage(
            location=settings.MEDIA_ROOT + folder
        )
        filename = fs.save(orig_filename, f)
        return {
            'filename': '{}{}'.format(folder, filename),
            'url': '{}{}{}'.format(settings.MEDIA_URL, folder,
                filename),
        }

    if request.method != 'POST':
        return HttpResponse(json.dumps({
            'success': False,
            'errors': ['POST, please.']
        }))

    images = [handle_uploaded_image(name, image) for name, image in
        request.FILES.items()]

    for image in images:
        image['thumb'] = get_thumbnail(image['filename'], '200x150',
            crop='center').url

    response = {
        'images': images
    }
    return HttpResponse(json.dumps(response))


@user_passes_test(lambda u: u.is_staff)
def xhr_update_photos(request):
    product = get_object_or_404(Product, pk=request.POST.get('pk', False))

    i = 1
    images = json.loads(request.POST['images'])
    existing = product.photos.all()
    new = []
    for image in images:
        photo, created = Photo.objects.get_or_create(image=image['filename'],
            product=product, defaults=dict(
                sort_index=99
            ))
        if image['selected']:
            photo.sort_index = 0
        else:
            photo.sort_index = i
            i += 1

        photo.save()
        new.append(photo)

    for e in existing:
        if e not in new:
            e.delete()

    response = {}
    return HttpResponse(json.dumps(response))


@user_passes_test(lambda u: u.is_staff)
def xhr_save_product(request, pk=None, type=None):
    if type == 'tablerow':
        cls = ProductTableRow
    else:
        cls = ProductForm
    if pk:
        try:
            p = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
        f = cls(request.POST, instance=p)

    else:
        f = cls(request.POST)

    if f.is_valid():
        product = f.save(commit=False)
        if not pk:
            slug = slugify(f.cleaned_data['name'])
            not_found = True
            product.slug = slug
            i = 2
            while not_found:
                try:
                    _ = Product.objects.get(slug=product.slug)
                except Product.DoesNotExist:
                    break
                product.slug = '{}-{}'.format(slug, i)
                i += 1

            product.num_views = 0
            product.in_date = datetime.datetime.utcnow()

        if product.sold and not product.sold_date:
            product.sold = datetime.date.today()

        product.save()

        return HttpResponse(json.dumps({
            'success': True,
            'pk': product.pk
        }))

    return HttpResponse(json.dumps({
        'success': False,
        'errors': f.errors
    }))


@user_passes_test(lambda u: u.is_staff)
def xhr_products(request):
    search_string = request.GET.get('q', '')
    # order_by = request.GET.get('order_by', None)
    # order = request.GET.get('order', None)
    output = []
    qs = Product.objects
    if len(search_string) > 0:
        qs = qsearch(qs, search_string)
    for product in qs.all():
        form = ProductTableRow(instance=product)
        if product.featured_photo:
            thumb_url = get_thumbnail(product.featured_photo.image,
                    '64x48', crop='center').url
        else:
            thumb_url = get_thumbnail(
                'product_photos/placeholder.png'.format(
                    settings.MEDIA_ROOT
                ),
                '64x48', crop='center').url
        product_row = {
            'id': product.id,
            'reference': product.reference,
            'name': product.name,
            'url': {
                'view': product.url,
                'edit': reverse('luxuryadmin:product', kwargs={
                    'product': product.id
                }),
                'save': reverse('luxuryadmin:xhr_save_product', kwargs={
                    'pk': product.id,
                    'type': 'tablerow'
                }),
                'thumb': thumb_url,
                'delete': reverse('luxuryadmin:xhr_delete_product', kwargs={
                    'product': product.id
                })
            },
            'num_views': product.num_views,
            'fields': {
                'featured': unicode(form['featured']),
                'category': unicode(form['category']),
                'sold': unicode(form['sold']),
                'live': unicode(form['live']),
            }
        }
        output.append(product_row)

    return HttpResponse(json.dumps(output), content_type='application/json')


def xhr_delete_product(request, product):
    product = get_object_or_404(Product, pk=product)
    product.delete()
    return HttpResponse("OK")

"""
Auth
"""
def xhr_log_in(request):
    form = LoginForm(request.POST)
    success = False
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                success = True

    return HttpResponse(json.dumps({
        'success': success
    }))


def log_out(request):
    logout(request)
    return redirect('/')
