from django.conf.urls import patterns, include, url

urlpatterns = patterns('collection.views',
    url(r'^(?P<category_slug>[-\w]*)/$', 'category', name='category'),
    url(r'^(?P<category_slug>[-\w]*)/sort/(?P<sort_by>[-\w]*)/$', 'category', name='category-sorted'),
    url(r'^(?P<category_slug>[-\w]*)/(?P<product_slug>[-\w]*)/$', 'product', name='product'),
    url(r'^$', 'category', name='category-home'),
)