import re
import datetime
from uuid import uuid4
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sorl.thumbnail import ImageField

from luxuryadmin.models import Company


class Category(models.Model):
    name = models.CharField(max_length=255)
    sort_index = models.IntegerField()
    slug = models.CharField(max_length=255)
    is_special = models.BooleanField()
    introduction_text = models.TextField(null=True)

    _num_products = None

    @property
    def products(self):
        return self.all_products.filter(live=True)

    @property
    def url(self):
        return reverse('collection:category', kwargs={
            'category_slug': self.slug
        })

    @property
    def num_products(self):
        if not self._num_products:
            self._num_products = self.products.filter(live=True).count()
        return self._num_products

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sort_index']
        verbose_name_plural = 'categories'


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='all_products')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    featured = models.BooleanField()
    sold = models.BooleanField()
    description = models.TextField(max_length=401)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    depth = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    price_gbp = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0.0'))
    price_usd = models.DecimalField(max_digits=8, decimal_places=2,
        null=True, blank=True)
    price_eur = models.DecimalField(max_digits=8, decimal_places=2,
        null=True, blank=True)
    in_date = models.DateTimeField(default=datetime.datetime.now())
    num_views = models.IntegerField(default=0, editable=False)
    live = models.BooleanField(default=True)
    reference = models.CharField(max_length=10,
        unique=True, blank=True, null=True)
    company = models.ForeignKey(Company, related_name='products',
        blank=True, null=True)

    sold_date = models.DateField(null=True, blank=True)
    cost_purchase = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0.0'), null=True, blank=True)
    cost_work = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0.0'), null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.sold and not self.sold_date:
            self.sold_date = datetime.date.today()
        super(Product, self).save(*args, **kwargs)

    @property
    def next(self):
        products = self.category.products.all()
        i = 0
        for product in products:
            if i == len(products):
                return False
            if product == self:
                try:
                    return products[i + 1]
                except IndexError:
                    return False
            i += 1

    @property
    def prev(self):
        products = self.category.products.all()

        i = 0
        for product in products:
            if product == self:
                if i == 0:
                    return False
                try:
                    return products[i - 1]
                except IndexError:
                    return False
            i += 1

    @property
    def excerpt(self):

        if not self.description:
            return ''
        excerpt = self.description[:440]

        patterns = [
            r'!?\[(.*)\]\((.*)\)',
            r'\*',
            r'#(.+)',
        ]

        for pattern in patterns:
            excerpt = re.sub(pattern, '', excerpt)

        if len(excerpt) > 140:
            ellip = u'\u2026'
        else:
            ellip = ''

        return excerpt[:140] + ellip

    @property
    def url(self):
        return reverse('collection:product', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug
        })

    @property
    def featured_photo(self):
        try:
            return self.photos.all()[0]
        except IndexError:
            return False

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-in_date']


@receiver(pre_save, sender=Product)
def update_ref(sender, instance, **kwargs):
    if not instance.reference:
        unique = False
        while not unique:
            instance.reference = str(uuid4())[:6].upper()
            try:
                test = Product.objects.get(reference=instance.reference)
            except Product.DoesNotExist:
                unique = True

class Photo(models.Model):
    image = ImageField(upload_to=settings.MEDIA_PATH['product'],
        null=True,
        blank=True)
    product = models.ForeignKey(Product, related_name='photos')
    sort_index = models.IntegerField()

    def __unicode__(self):
        return '%s photo #%s' % (self.product.name, self.sort_index)

    class Meta:
        ordering = ['sort_index']
