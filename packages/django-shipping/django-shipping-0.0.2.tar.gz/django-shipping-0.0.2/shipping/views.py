# coding: utf-8
import json
import logging
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, Http404
from shipping.models import Country, State


def countries(request):
    countries = Country.objects.filter(zone__status=1).filter(status=1)\
        .order_by('name')

    response = {'countries': []}
    for country in countries:
        response['countries'].append({'iso': country.iso, 'name': country.name})

    return HttpResponse(json.dumps(response), mimetype="application/json;charset=utf-8")


def states(request, country_code):
    country = get_object_or_404(Country, iso=country_code)
    states = country.states.order_by('name').all()

    response = {'states': []}
    for state in states:
        response['states'].append({'iso': state.iso, 'name': state.name, 'id': state.id})

    return HttpResponse(json.dumps(response), mimetype="application/json;charset=utf-8")


@csrf_protect
def estimation(request):
    dimensions = request.POST.getlist('dimensions')
    zipcode = request.POST.get('zipcode')
    state = request.POST.get('state')

    country_code = request.POST.get('country_code')

    country = get_object_or_404(Country, iso=country_code)
    if state:
        state = get_object_or_404(State, id=state)

    if len(dimensions) < 1:
        raise Http404()

    try:
        carrier = country.zone.get_carrier()
        price = carrier.estimate_shipping(dimensions, country, state, zipcode)

        response = json.dumps({'price': price})
    except:
        logging.exception('oops, problem when estimate shipping')
        response = json.dumps({'error': "your country's carrier is unavailable"})

    return HttpResponse(response, mimetype="application/json;charset=utf-8")
