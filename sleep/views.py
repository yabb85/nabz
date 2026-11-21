from django.shortcuts import render
from .models import Sleep
from datetime import datetime, timedelta, time
from django.http import HttpResponse, Http404, FileResponse
from django.db.models import Q
from vl.utils import send
from xml.etree.ElementTree import Element, SubElement, tostring
from scheduler.models import Schedule
from .forms import SleepForm
from django.views.generic.edit import FormView
from vl.models import Bunny
from pathlib import Path
from random import choice
from pytz import timezone

CUR_DIR = Path(__file__).parent


# Create your views here.
def index(request):
    sleep = Sleep.objects.filter(bunny__user=request.user)
    context = {'sleep_confs': sleep}
    return render(request, 'sleep/index.html', context)


class SleepEditView(FormView):
    template_name = 'sleep/edit.html'
    form_class = SleepForm
    success_url = '/sleep/'

    # def get_success_url(self):
    # return self.success_url + self.sn

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.bunny = Bunny.objects.get(sn=self.sn)
        response = super().form_valid(form)
        form.save()
        return response

    def get(self, request, sn, *args, **kwargs):
        self.sn = sn
        conf = Sleep.objects.filter(bunny__sn__contains=sn)
        if conf:
            form = self.form_class(instance=conf[0])
        else:
            form = self.get_form()
        context = {'form': form}
        return render(request, 'sleep/edit.html', context)

    def post(self, request, sn, *args, **kwargs):
        self.sn = sn
        conf = Sleep.objects.filter(bunny__sn__contains=sn)
        if conf:
            form = self.form_class(request.POST, instance=conf[0])
        else:
            form = self.get_form()
            form.instance.user = self.request.user
        response = self.form_valid(form)
        update_scheduler(request)
        return response


def one_click(request):
    sn = request.GET.get('sn', None)
    conf = Sleep.objects.get(bunny__sn__contains=sn)
    print(conf)


def double_click(request):
    sn = request.GET.get('sn', None)
    conf = Sleep.objects.get(bunny__sn__contains=sn)
    print(conf)


def cron(request):
    url_base = request.build_absolute_uri('sound/')
    sleep_list = Sleep.objects.all()
    for sleep in sleep_list:
        tz = sleep.bunny.time_zone
        now = datetime.now(tz=timezone(tz))
        day = now.weekday()
        limite_hour = (now - timedelta(minutes=1)).time()
        col_sleep, col_wake_up = get_columns(day)
        q_sleep_b = get_condition(col_sleep, now.time(), 'lte')
        q_wake_up_b = get_condition(col_wake_up, now.time(), 'lte')
        after = (now - timedelta(minutes=1)).time()
        q_sleep_a = get_condition(col_sleep, after, 'gt')
        q_wake_up_a = get_condition(col_wake_up, after, 'gt')
        sleep_exec = (
            Sleep.objects.filter(bunny=sleep.bunny)
            .filter(q_sleep_b | q_wake_up_b)
            .filter(q_sleep_a | q_wake_up_a)
            .order_by(col_sleep, col_wake_up)
            .only('bunny', col_sleep, col_wake_up)
            .first()
        )
        if sleep_exec:
            sleep_hour = getattr(sleep_exec, col_sleep, None)
            wake_up_hour = getattr(sleep_exec, col_wake_up, None)
            if sleep_hour <= now.time() and sleep_hour > limite_hour:
                action(sleep.bunny.sn, 'sleep', url_base)
            elif wake_up_hour <= now.time() and wake_up_hour > limite_hour:
                action(sleep.bunny.sn, 'wakeup', url_base)
    update_scheduler(request)
    return HttpResponse('ok')


def sound(request, name):
    mp3_path = None
    dir_path = CUR_DIR.joinpath('sounds', 'fr_FR', name)
    list_files = list(dir_path.glob('*'))
    dir_path = CUR_DIR.joinpath('sounds', name)
    list_files.extend(list(dir_path.glob('*')))
    print(f'list_files:  {list_files}')
    mp3_path = choice(list_files)
    print(f'mp3_path: {mp3_path}')
    try:
        response = FileResponse(open(mp3_path, 'rb'))
        response['content_type'] = 'audio/mpeg'
        return response
    except Exception as e:
        print(e)
        raise Http404


def get_columns(day):
    conversion = {
        0: 'monday',
        1: 'tuesday',
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday',
    }
    plop = conversion[day]
    return (plop + '_sleep', plop + '_wake_up')


def get_condition(column: str, value: time, condition: str):
    kwargs = {f'{column}__{condition}': value}
    return Q(**kwargs)


def update_scheduler(request):
    """
    Update scheduler with next execution date
    """
    s = Schedule.objects.filter(service='sleep')
    if not s:
        s = Schedule(service='sleep', url=str(request.build_absolute_uri()))
    else:
        s = s[0]
    sleep_list = Sleep.objects.all()
    next_date = None
    for sleep in sleep_list:
        tz = sleep.bunny.time_zone
        now = datetime.now(tz=timezone(tz))
        tmp_date = get_next_date(sleep, now)
        if not next_date:
            next_date = tmp_date
        else:
            next_date = min(next_date, tmp_date)
    s.datetime = next_date
    s.save()


def get_next_hour_of_the_day(sleep, now, next_time=None):
    """
    Search the next time registered for the current day in sleep entry
    """
    day = now.weekday()
    col_sleep, col_wake_up = get_columns(day)
    sleep_hour = getattr(sleep, col_sleep, None)
    wake_up_hour = getattr(sleep, col_wake_up, None)
    if sleep_hour and sleep_hour > now.time():
        if next_time:
            next_time = min(next_time, sleep_hour)
        else:
            next_time = sleep_hour
    if wake_up_hour and wake_up_hour > now.time():
        if next_time:
            next_time = min(next_time, wake_up_hour)
        else:
            next_time = wake_up_hour
    return next_time

def get_next_date(sleep, now):
    """
    Search the next date available in current sleep entry
    """
    next_time = get_next_hour_of_the_day(sleep, now)
    if not next_time:
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        next_time = get_next_hour_of_the_day(sleep, tomorrow)
        date = datetime.combine(tomorrow.date(), next_time)
    else:
        date = datetime.combine(now.date(), next_time)
    return date


def action(sn: str, action: str, url_base: str):
    """
    Send message to change sleep state and update database
    """
    url = url_base + action
    bunny = Bunny.objects.get(sn=sn)
    bunny.sleep_state = action == 'sleep'
    bunny.save()
    order = Element('order')
    order.set('sn', sn)
    if 'sleep' == action:
        block = SubElement(order, 'block')
        block.text = f'MU {url}\nMW\n'
        ambiant = SubElement(order, 'ambiant')
        sleep = SubElement(ambiant, 'sleep')
    else:
        ambiant = SubElement(order, 'ambiant')
        sleep = SubElement(ambiant, 'sleep')
        block = SubElement(order, 'block')
        block.text = f'MU {url}\nMW\n'
    sleep.text = action
    send(tostring(order))
