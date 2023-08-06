# coding: utf-8
from django import template
from shipping.models import Country

register = template.Library()


@register.inclusion_tag('shipping/freight.html', takes_context=True)
def shipping_freight(context):
    countries = Country.objects.filter(zone__status=1).filter(status=1)\
        .filter(zone__isnull=False).distinct().order_by('name')

    context.update({'countries': countries})

    return context
