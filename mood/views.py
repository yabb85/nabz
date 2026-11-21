"""
Module to add mood on bunny
The bunny have activity following frequency parameter.

Usage:
- choose frequency on settings
"""


from django.shortcuts import render
from django.http import Http404, FileResponse, HttpResponse
from .models import Mood, Frequency
from datetime import timedelta, datetime
from random import randint
from pytz import UTC
from pathlib import Path
from random import choice
from xml.etree.ElementTree import Element, SubElement, tostring
from vl.utils import send
from scheduler.models import Schedule

CUR_DIR = Path(__file__).parent


# Create your views here.
def index(request):
    mood = Mood.objects.filter(bunny__user=request.user)
    context = {
        'mood_confs': mood,
    }
    return render(request, 'mood/index.html', context)


def cron(request):
    url_base = request.build_absolute_uri('sound/')
    mood = Mood.objects.filter(next_date__lte=datetime.now(tz=UTC)).order_by('next_date').first()
    print(mood)
    if mood:
        limit = max(datetime.now(tz=UTC), mood.next_date)
        limit = limit + timedelta(minutes=5)
        print(limit)
        other_mood = Mood.objects.filter(enabled=True).filter(next_date__lte=limit).all()
        print(other_mood)
        for mood in other_mood:
            next_time = next_iteration(limit, mood.frequency)
            print(next_time)
            if not mood.bunny.sleep_state:
                action(mood.bunny.sn, url_base)
            mood.next_date = next_time
            mood.save()
        update_scheduler(request)
    return HttpResponse('ok')


def next_iteration(time: datetime, frequency: int) -> datetime:
    if frequency == Frequency.VERY_OFTEN.numerator:
        delta = timedelta(seconds=randint(0, frequency))
    elif frequency == Frequency.OFTEN.numerator:
        delta = timedelta(seconds=randint(Frequency.VERY_OFTEN.numerator, frequency))
    elif frequency== Frequency.SOMETIMES.numerator:
        delta = timedelta(seconds=randint(Frequency.OFTEN.numerator, frequency))
    elif frequency== Frequency.RARELY.numerator:
        delta = timedelta(seconds=randint(Frequency.SOMETIMES.numerator, frequency))
    elif frequency== Frequency.VERY_RARELY.numerator:
        delta = timedelta(seconds=randint(Frequency.RARELY.numerator, frequency))
    else:
        raise Exception('Frequency not known')
    next_time = time + delta
    return next_time


def sound(request):
    mp3_path = None
    lang = request.GET.get('lang', 'fr_FR')
    dir_path = CUR_DIR.joinpath('sounds', lang)
    list_files = list(dir_path.glob('*'))
    mp3_path = choice(list_files)
    print(f'mp3_path: {mp3_path}')
    try:
        response = FileResponse(open(mp3_path, 'rb'))
        response['content_type'] = 'audio/mpeg'
        return response
    except Exception as e:
        print(e)
        raise Http404


def update_scheduler(request):
    s = Schedule.objects.filter(service='mood')
    if not s:
        s = Schedule(service='mood', url=str(request.build_absolute_uri()))
    else:
        s = s[0]
    mood = Mood.objects.filter(enabled=True).order_by('next_date').first()
    s.datetime = mood.next_date
    s.save()


def action(sn: str, url_base: str):
    print(sn)
    url = url_base
    order = Element('order')
    order.set('sn', sn)
    block = SubElement(order, 'block')
    block.text = f'MU {url}\nMW\n'
    send(tostring(order))
