from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import render
from meteofrance_api import MeteoFranceClient
from pathlib import Path
from vl.utils import send
from xml.etree.ElementTree import Element, SubElement, tostring
from .models import Weather
from datetime import datetime
from django.views.generic import FormView
from .forms import WeatherForm
from django.db.models import Q
from time import sleep


CUR_DIR = Path(__file__).parent


WEATHER_CONVERSION = {
    "Eclaircies": ("sunny", 0),
    "Peu nuageux": ("sunny", 0),
    "Ensoleillé": ("sunny", 0),
    "Ciel clair": ("sunny", 0),
    "Ciel voilé": ("cloudy", 1),
    "Ciel voilé nuit": ("cloudy", 1),
    "Très nuageux": ("cloudy", 1),
    "Couvert": ("cloudy", 1),
    "Rares averses": ("rainy", 3),
    "Averses": ("rainy", 3),
    "Averses faibles": ("rainy", 3),
    "Pluies éparses": ("rainy", 3),
    "Pluie": ("rainy", 3),
    "Pluie modérée": ("rainy", 3),
    "Pluie faible": ("rainy", 3),
    "Pluie forte": ("rainy", 3),
    "Risque de grêle": ("rainy", 3),
    "Risque de grèle": ("rainy", 3),
    "Bruine / Pluie faible": ("rainy", 3),
    "Bruine": ("rainy", 3),
    "Pluies éparses / Rares averses": ("rainy", 3),
    "Pluie / Averses": ("rainy", 3),
    "Pluie et neige mêlées": ("snowy", 4),
    "Neige / Averses de neige": ("snowy", 4),
    "Neige": ("snowy", 4),
    "Averses de neige": ("snowy", 4),
    "Neige forte": ("snowy", 4),
    "Quelques flocons": ("snowy", 4),
    "Pluie et neige": ("snowy", 4),
    "Pluie verglaçante": ("snowy", 4),
    "Brume ou bancs de brouillard": ("foggy", 2),
    "Bancs de Brouillard": ("foggy", 2),
    "Brouillard": ("foggy", 2),
    "Brouillard givrant": ("foggy", 2),
    "Brume": ("foggy", 2),
    "Pluies orageuses": ("stormy", 5),
    "Pluie orageuses": ("stormy", 5),
    "Orages": ("stormy", 5),
    "Averses orageuses": ("stormy", 5),
    "Risque d'orages": ("stormy", 5),
}


# Create your views here.
def index(request):
    weather = Weather.objects.filter(Q(bunny__user=request.user) | Q(zstamp__user=request.user)).all()
    print(weather)
    context = {
        'weather_confs': weather
    }
    return render(request, 'weather/index.html', context)


class WeatherEditView(FormView):
    template_name = 'weather/edit.html'
    form_class = WeatherForm
    success_url = '/weather/'

    def get(self, request, pk=None, *args, **kwargs):
        conf = Weather.objects.filter(pk=pk).first()
        print(conf)
        if conf:
            form = self.form_class(instance=conf)
        else:
            form = self.form_class(user=request.user)
        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


def one_click(request):
    sn = request.GET.get('sn', None)
    conf = Weather.objects.get(bunny__sn__contains=sn, action='oneclick')
    url_base = request.build_absolute_uri('sound/')
    temp = action(sn, url_base, conf.city, conf.type)
    return HttpResponse(temp)


def double_click(request):
    sn = request.GET.get('sn', None)
    conf = Weather.objects.get(bunny__sn__contains=sn, action='doubleclick')
    url_base = request.build_absolute_uri('sound/')
    temp = action(sn, url_base, conf.city, conf.type)
    return HttpResponse(temp)

def rfid(request):
    sn = request.GET.get('sn', None)
    z_serial = request.GET.get('serial', None)
    conf = Weather.objects.get(zstamp__serial__contains=z_serial, action='rfid')
    url_base = request.build_absolute_uri('sound/')
    temp = action(sn, url_base, conf.city, conf.type)
    return HttpResponse(temp)


def action(sn: str, url_base: str, city: str, when: str):
    client = MeteoFranceClient()
    city = client.search_places(city)[0]
    my_place_weather_forecast = client.get_forecast_for_place(city)
    now = datetime.now()
    if when == 'now':
        my_place_current_forecast = my_place_weather_forecast.current_forecast
        temp = float(my_place_current_forecast['T']['value'])
        sky = None
    elif when == 'today':
        if now.hour >= 18:
            my_place_forecast = my_place_weather_forecast.daily_forecast[1]
            when = 'tomorrow'
        else:
            my_place_forecast = my_place_weather_forecast.today_forecast
        temp = float(my_place_forecast['T']['max'])
        sky = my_place_forecast['weather12H']['desc']
    url_sig = url_base + 'signature.mp3'
    url_when = url_base + when + '.mp3'
    url_temp = url_base + str(int(temp)) + '.mp3'
    url_deg = url_base + 'degree.mp3'
    order = Element('order')
    order.set('sn', sn)
    block = SubElement(order, 'block')
    if sky:
        ambiant = SubElement(order, 'ambiant')
        weather = SubElement(ambiant, 'weather')
        file_name, id_weather = WEATHER_CONVERSION[sky]
        url_sky = url_base + file_name + '.mp3'
        weather.text = f'{id_weather}'
        data = f'MU {url_sig}\nMW\nMU {url_when}\nMW\nMU {url_sky}\nMW\nMU {url_temp}\nMW\nMU {url_deg}\nMW\n'
    else:
        data = f'MU {url_sig}\nMW\nMU {url_temp}\nMW\nMU {url_deg}\nMW\n'
    block.text = data
    send(tostring(order))
    if sky:
        sleep(120)
        order = Element('order')
        order.set('sn', sn)
        ambiant = SubElement(order, 'ambiant')
        disable = SubElement(ambiant, 'disable')
        disable.text = '1'
        send(tostring(order))
    return temp


def sound(request, name):
    mp3_path = None
    dir_path = CUR_DIR.joinpath('sounds', 'fr_FR')
    files_path = dir_path.glob('**/' + name)
    for file in files_path:
        mp3_path = file
    if not mp3_path:
        dir_path = CUR_DIR.joinpath('sounds', 'nabweatherd')
        files_path = dir_path.glob('**/' + name)
        for file in files_path:
            mp3_path = file
    try:
        response = FileResponse(open(mp3_path, 'rb'))
        response['content_type'] = 'audio/mpeg'
        return response
    except Exception:  # TODO: define better exception
        raise Http404
