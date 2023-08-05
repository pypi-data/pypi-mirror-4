from django.http import Http404
from django.template.response import TemplateResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Product, Category
from .utils import Struct

from luxuryadmin.utils import qsearch

@ensure_csrf_cookie
def category(request, category_slug=None, sort_by=None):

    qs = Product.objects.filter(live=True)
    if len(request.GET.get('q', '')) > 0:
        qs = qsearch(qs, request.GET['q'])
        category = None
    else:
        try:
            if not category_slug:
                category = Category.objects.all()[0]
            else:
                category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404
        qs = qs.filter(category=category)
    if sort_by == 'price':
        qs = qs.order_by('price_gbp')
    elif sort_by == 'price-desc':
        qs = qs.order_by('-price_gbp')
    else:
        sort_by = 'recent'


    context = { 'category': category
              , 'products': qs.all()
              , 'sort_by': sort_by
              , 'page': Struct(slug='collection', title='Collection')
              , 'last_search': request.GET.get('q', '')
              }
    return TemplateResponse(request, 'collection.html', context)


@ensure_csrf_cookie
def product(request, category_slug=None, product_slug=None):
    try:
        category = Category.objects.get(slug=category_slug)
        product = Product.objects.get(slug=product_slug)
        products = category.products.all()
    except (Category.DoesNotExist, Product.DoesNotExist):
        raise Http404

    product.num_views += 1
    product.save()

    i = 0
    product_index = 0
    for p in products:
        if p == product:
            product_index = i
        i += 1

    context = {
        'product': product,
        'products': products,
        'product_index': product_index,
        'category': category,
        'page': Struct(slug='collection', title='Collection'),
    }
    return TemplateResponse(request, 'product.html', context)
