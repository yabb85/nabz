"""
Module to have hour, say a message each hour.
"""


from django.shortcuts import render
from .models import Clock
from pathlib import Path
from django.http import Http404, FileResponse, HttpResponse
from random import choice
from datetime import datetime, timedelta
from scheduler.models import Schedule
from vl.utils import send
from xml.etree.ElementTree import Element, SubElement, tostring
from django.views.generic.edit import FormView
from .forms import ClockForm


CUR_DIR = Path(__file__).parent


# Create your views here.
def index(request):
    clocks = Clock.objects.filter(bunny__user=request.user)
    context = {
        'clocks': clocks,
    }
    return render(request, 'clock/index.html', context)


class ClockEditView(FormView):
    template_name = 'clock/index.html'
    form_class = ClockForm
    success_url = '/clock/'

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

    def get(self, request, pk=None, *args, **kwargs):
        conf = Clock.objects.filter(pk=pk)
        if conf:
            form = self.form_class(instance=conf[0])
        else:
            form = self.get_form()
        context = {
            'form': form,
        }
        return render(request, 'clock/edit.html', context)

    def post(self, request, pk=None):
        conf = Clock.objects.filter(pk=pk)
        if conf:
            form = self.form_class(request.POST, instance=conf[0])
        else:
            form = self.get_form()
        return self.form_valid(form)



def cron(request):
    s = Schedule.objects.filter(service='clock')
    if not s:
        s = Schedule(service='clock', url=str(request.build_absolute_uri()))
    else:
        s = s[0]
    now = datetime.now()
    next_date = now + timedelta(hours=1)
    next_date = next_date.replace(minute=0, second=0, microsecond=0)
    s.datetime = next_date
    s.save()
    url_base = request.build_absolute_uri('sound/')
    exec_list = Clock.objects.filter(enabled=True)
    for exe in exec_list:
        if not exe.bunny.sleep_state:
            action(exe.bunny.sn, url_base)
    return HttpResponse('ok')


def sound(request, name):
    lang = request.GET.get('lang', 'fr_FR')
    mp3_path = None
    dir_path = CUR_DIR.joinpath('sounds', lang, name)
    list_files = list(dir_path.glob('*'))
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


def action(sn: str, url_base: str):
    now = datetime.now().time()
    url = url_base + str(now.hour)
    order = Element('order')
    order.set('sn', sn)
    block = SubElement(order, 'block')
    block.text = f'MU {url}\nMW\n'
    send(tostring(order))
