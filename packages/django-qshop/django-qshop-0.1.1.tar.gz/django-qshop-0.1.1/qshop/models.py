from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item
from .qshop_settings import PRODUCT_CLASS, VARIATION_CLASS, VARIATION_VALUE_CLASS, PRODUCT_IMAGE_CLASS, PARAMETERS_SET_CLASS, PARAMETER_CLASS, PARAMETER_VALUE_CLASS, PRODUCT_TO_PARAMETER_CLASS

Menu = import_item(MENUCLASS)


class PricingModel:
    def _get_price(self):
        return self.price

    def _get_discount_price(self):
        return self.discount_price

    def has_discount(self):
        if self._get_discount_price():
            return True
        else:
            return False

    def get_price(self):
        if self.has_discount():
            return Currency.get_price(self._get_discount_price())
        return Currency.get_price(self._get_price())

    def get_price_real(self):
        return Currency.get_price(self._get_price())

    def get_price_discount(self):
        return Currency.get_price(self._get_discount_price())

    def get_fprice(self):
        return Currency.get_fprice(self.get_price(), True)

    def get_fprice_real(self):
        return Currency.get_fprice(self.get_price_real(), True)

    def get_fprice_discount(self):
        return Currency.get_fprice(self.get_price_discount(), True)

    def get_discount_percent(self):
        discount = self.get_price_discount()
        if not discount:
            return 0
        else:
            return "%.0f" % (self.get_price_discount() * 100 / self.get_price_real() - 100)


class ProductAbstract(models.Model, PricingModel):

    selected_variation = None

    SORT_VARIANTS = (
        ('natural', 'sort', _('natural')),
        ('price_asc', 'price', _('price low to high')),
        ('price_desc', '-price', _('price high to low')),
        ('name', 'name', _('by name')),
    )

    has_variations = models.BooleanField(default=False, editable=False)
    parameters_set = models.ForeignKey('ParametersSet', verbose_name=_('parameters set'))
    articul = models.SlugField(_('articul'))
    name    = models.CharField(_('name'), max_length=128)
    price = models.DecimalField(_('price'), max_digits=12, decimal_places=2)
    weight = models.FloatField(_('weight'), default=0, blank=True)
    discount_price = models.DecimalField(_('discount price'), max_digits=12, decimal_places=2, blank=True, null=True)
    description = models.TextField(_('description'), default='', blank=True)
    image = ThumbnailerImageField(_('image'), upload_to='products/main', blank=True, resize_source=dict(size=(1024, 1024)))

    category = models.ManyToManyField(Menu, verbose_name=_('category'))

    parameters = models.ManyToManyField('Parameter', through='ProductToParameter', verbose_name=_('parameters'))

    sort = models.IntegerField(_('sort'), default=0)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['sort']
        abstract = True

    def __unicode__(self):
        return "%s (articul: %s)" % (self.name, self.articul)

    def get_absolute_url(self):
        try:
            return self.absolute_url
        except:
            category = self.get_current_category()
            self.absolute_url = reverse('dispatcher', kwargs={'url': "%s%s/" % (category.full_url, self.articul)})
            return self.absolute_url

    def get_current_category(self):
        try:
            return self._current_category
        except:
            self._current_category = self.category.all()[0]
            return self._current_category

    def __init__(self, *args, **kwargs):
        super(ProductAbstract, self).__init__(*args, **kwargs)
        self.old_parameters_set_id = self.parameters_set_id

    # def save(self, skip_variations=False, *args, **kwargs):
    #     super(Product, self).save(*args, **kwargs)

    def _get_price(self):
        if self.selected_variation:
            return self.selected_variation.price
        return self.price

    def _get_discount_price(self):
        if self.selected_variation:
            return self.selected_variation.discount_price
        return self.discount_price

    def select_variation(self, variation_id):
        if not self.has_variations:
            return False
        try:
            variation = ProductVariation.objects.get(pk=variation_id)
        except ProductVariation.DoesNotExist:
            variation = ProductVariation.objects.filter(product=self)[0]
        self.selected_variation = variation
        return True

    def has_parameters(self):
        if self._get_parameters_for_product():
            return True
        return False

    def get_parameters(self):
        try:
            return self._parameters_list
        except:
            pass

        ret = []
        for item in self._get_parameters_for_product():
            ret.append({
                'id': item.value_id,
                'name': item.parameter.name,
                'value': item.value.value
            })

        self._parameters_list = ret
        return self._parameters_list

    def _get_parameters_for_product(self):
        try:
            return self._parameters_for_product
        except:
            self._parameters_for_product = ProductToParameter.objects.select_related('parameter', 'value').filter(product=self).exclude(value=None)
            return self._parameters_for_product

    def get_additional_images(self):
        try:
            return self._additional_images
        except:
            self._additional_images = self.productimage_set.all()
        return self._additional_images

    def is_parametrs_set_changed(self):
        if self.old_parameters_set_id != self.parameters_set_id:
            return True
        return False

    def get_variations(self):
        try:
            return self._get_variations
        except:
            self._get_variations = self.productvariation_set.all()
            return self._get_variations


class ProductVariationValueAbstract(models.Model):
    value = models.CharField(_('name'), max_length=128)

    class Meta:
        verbose_name = _('product variation value')
        verbose_name_plural = _('product variation values')
        ordering = ['value']
        abstract = True

    def __unicode__(self):
        return "%s" % self.value


class ProductVariationAbstract(models.Model, PricingModel):
    product = models.ForeignKey('Product')
    variation = models.ForeignKey('ProductVariationValue')
    price = models.DecimalField(_('price'), max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(_('discount price'), max_digits=12, decimal_places=2, blank=True, null=True)
    sort = models.IntegerField(_('sort'), default=0)

    class Meta:
        verbose_name = _('product variation')
        verbose_name_plural = _('product variations')
        ordering = ['sort']
        abstract = True

    def save(self, skip_variations=False, *args, **kwargs):
        super(ProductVariationAbstract, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.price

    @property
    def name(self):
        return self.variation.value


class ProductImageAbstract(models.Model):
    image = ThumbnailerImageField(_('image'), upload_to='products/more', resize_source=dict(size=(1024, 1024)))
    product = models.ForeignKey('Product')

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        abstract = True

    def __unicode__(self):
        return "%s" % self.image


class ParametersSetAbstract(models.Model):
    name = models.CharField(_('name'), max_length=64)

    class Meta:
        verbose_name = _('parameters set')
        verbose_name_plural = _('parameters sets')
        abstract = True

    def __unicode__(self):
        return self.name


class ParameterAbstract(models.Model):
    parameters_set = models.ForeignKey('ParametersSet')
    name = models.CharField(_('name'), max_length=128)
    is_filter = models.BooleanField(_('is filter'), default=True)
    order = models.IntegerField(_('order'))

    class Meta:
        ordering = ['order']
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        abstract = True

    def __unicode__(self):
        return self.name


class ParameterValueAbstract(models.Model):
    parameter = models.ForeignKey('Parameter')
    value = models.CharField(_('parameter value'), max_length=128)

    class Meta:
        unique_together = (("parameter", "value"),)
        verbose_name = _('parameter value')
        verbose_name_plural = _('parameter values')
        abstract = True

    def __unicode__(self):
        return self.value


class ProductToParameterAbstract(models.Model):
    product = models.ForeignKey('Product')
    parameter = models.ForeignKey('Parameter')
    value = models.ForeignKey('ParameterValue', blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return 'Product Field Nr. %d' % self.parameter_id

# Create real classes


class Product(import_item(PRODUCT_CLASS) if PRODUCT_CLASS else ProductAbstract):
    pass


class ProductVariationValue(import_item(VARIATION_VALUE_CLASS) if VARIATION_VALUE_CLASS else ProductVariationValueAbstract):
    pass


class ProductVariation(import_item(VARIATION_CLASS) if VARIATION_CLASS else ProductVariationAbstract):
    pass


class ProductImage(import_item(PRODUCT_IMAGE_CLASS) if PRODUCT_IMAGE_CLASS else ProductImageAbstract):
    pass


class ParametersSet(import_item(PARAMETERS_SET_CLASS) if PARAMETERS_SET_CLASS else ParametersSetAbstract):
    pass


class Parameter(import_item(PARAMETER_CLASS) if PARAMETER_CLASS else ParameterAbstract):
    pass


class ParameterValue(import_item(PARAMETER_VALUE_CLASS) if PARAMETER_VALUE_CLASS else ParameterValueAbstract):
    pass


class ProductToParameter(import_item(PRODUCT_TO_PARAMETER_CLASS) if PRODUCT_TO_PARAMETER_CLASS else ProductToParameterAbstract):
    pass


class Currency(models.Model):
    code = models.CharField(_('code'), max_length=3, db_index=True)
    name = models.CharField(_('currency name'), max_length=12)
    rate = models.FloatField(_('rate'))
    sort = models.SmallIntegerField(_('order'))
    show_string = models.CharField(max_length=16)

    current_currency = None

    class Meta:
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')
        ordering = ('sort',)

    def __unicode__(self):
        return self.code

    @staticmethod
    def get_price(price):
        return float(price) / Currency.get_default_currency().rate

    @staticmethod
    def get_fprice(price, format_only=False):
        if not format_only:
            price = Currency.get_default_currency().get_price(price)
        return mark_safe(unicode(Currency.get_default_currency().show_string) % price)

    @staticmethod
    def get_default_currency():
        if not Currency.current_currency:
            Currency.current_currency = Currency.objects.all()[0]
        return Currency.current_currency
