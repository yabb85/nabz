from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponseRedirect, HttpResponse
from .utils import send
from .forms import BunnyForm, BunnyEditForm, ZStampEditForm
from vl.models import ZStamp, Bunny, Plugin
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from datetime import datetime


IPAddr = 'tofu'
# IPAddr = '192.168.1.21'

# Create your views here.

def bc(request):
    print(bc)
    print(request)
    try:
        # response = FileResponse(open('static/bootcode.ojn', 'rb'))
        response = FileResponse(open('static/bootcode.bin', 'rb'))
        response['content_type'] = 'application/octet-stream'
        print(response)
        return response
    except Exception:  # TODO: use better exception
        raise Http404


def locate(request):
    sn = request.GET.get('sn', None)
    h = request.GET.get('h', None)
    v = request.GET.get('v', None)
    print(sn)
    print(h)
    print(v)
    data = f'ping {IPAddr}\nbroad {IPAddr}\nxmpp_domain {IPAddr}\n'
    return HttpResponse(data)


def rfid(request):
    sn = request.GET.get('sn', None)
    h = request.GET.get('h', None)
    v = request.GET.get('v', None)
    t = request.GET.get('t', None)
    print(h)
    print(v)
    print(t)
    zstamp = ZStamp.objects.filter(serial=t).first()
    print(zstamp)
    if not zstamp:
        bunny = Bunny.objects.get(sn=sn)
        zstamp = ZStamp(serial=t, user=bunny.user)
        zstamp.save()
    else:
        if zstamp and zstamp.plugin:
            url_new = request.build_absolute_uri('/' + zstamp.plugin + f'/rfid?sn={sn}&serial={t}')
            return HttpResponseRedirect(url_new)  # return full url instead of partial because not supported by nabaztag
    return HttpResponse('ok')


@csrf_exempt
def record(request):
    sn = request.GET.get('sn', None)
    bunny = Bunny.objects.get(sn=sn)
    if bunny.plugin_record:
        raw_data = BytesIO(request.body)
        str_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'record_{sn}_{str_date}.wav'
        with open(filename, 'wb') as test:
            test.write(raw_data.read())
        url_new = request.build_absolute_uri('/' + bunny.plugin_record.name + f'/record?sn={sn}&name={filename}')
    return HttpResponseRedirect(url_new)


def itmode(request):
    return HttpResponse('ok')


def send_mail_xmpp(request):
    """
    Called when login fail send mail to prevent user off login failed
    """
    mac = request.GET.get('m', None)
    print(mac)


#
# Customized urls to send order
#

def order(request):
    sn = request.GET.get('sn', None)
    order = request.GET.get('r', None)
    if not order:
        # order = 'ST http://tofu/static/plugins/book/fr_FR/9782070548064/2.mp3\nMW\n'
        # msg = f'<order sn="{sn}"><ambiant><sleep>wakeup</sleep></ambiant></order>'
        # msg = f'<order sn="{sn}"><ambiant><sleep>sleep</sleep></ambiant></order>'
        msg = f'<order sn="{sn}"><ambiant><ears><right>0</right><left>0</left></ears></ambiant></order>'
    else:
        msg = f'<order sn="{sn}"><block>{order}</block></order>'
    send(msg.encode())
    # url_base = request.build_absolute_uri('/sleep/sound/')
    # action(sn, 'wakeup', url_base)
    return HttpResponse('ok')


def mp3(request, filename):
    try:
        response = FileResponse(open(f'static/{filename}', 'rb'))
        response['content_type'] = 'application/octet-stream'
        return response
    except Exception:  # TODO: use better exception
        pass


def one_click(request):
    sn = request.GET.get('sn', None)
    if sn:
        bunny = Bunny.objects.get(sn=sn)
        if bunny:
            if bunny.plugin_active:
                plugin = bunny.plugin_active.name
            elif bunny.one_click:
                plugin = bunny.one_click.name
            else:
                return HttpResponse('not activated')
            url_new = request.build_absolute_uri(f'/{plugin}/oneclick?sn={sn}')
            return HttpResponseRedirect(url_new)  # return full url instead of partial because not supported by nabaztag
    else:
        raise Exception('missing sn param')
    # return HttpResponse('ok')


def double_click(request):
    sn = request.GET.get('sn', None)
    if sn:
        bunny = Bunny.objects.get(sn=sn)
        if bunny:
            if bunny.plugin_active:
                plugin = bunny.plugin_active.name
            elif bunny.one_click:
                plugin = bunny.one_click.name
            else:
                return HttpResponse('not activated')
            url_new = request.build_absolute_uri(f'/{plugin}/doubleclick?sn={sn}')
            return HttpResponseRedirect(url_new)  # return full url instead of partial because not supported by nabaztag
    else:
        raise Exception('missing sn param')
    # return HttpResponse('ok')


def ears_move(request):
    sn = request.GET.get('sn', None)
    left = request.GET.get('left', None)
    right = request.GET.get('right', None)
    bunny = Bunny.objects.get(sn=sn)
    if bunny and bunny.plugin_active:
        url_new = request.build_absolute_uri('/' + bunny.plugin_active.name + f'/earsmove?sn={sn}&left={left}&right={right}')
        return HttpResponseRedirect(url_new)
    else:
        return Http404


#
# Views to disaply information on website
#

@login_required
def bunny(request):
    bunnies = Bunny.objects.filter(user=request.user)
    context = {
        'bunnies': bunnies,
        'form': BunnyForm(),
    }
    return render(request, 'bunny.html', context)


class BunnyEditView(FormView):
    template_name = 'bunny_details.html'
    form_class = BunnyEditForm
    success_url = '/vl/bunny'

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

    def get(self, request, sn):
        bunny = Bunny.objects.filter(sn=sn).first()
        form = self.form_class(instance=bunny)

        context = {
            'form': form
        }
        return render(request, 'bunny_details.html', context)

    def post(self, request, sn):
        bunny = Bunny.objects.filter(sn=sn).first()
        if bunny:
            form = self.form_class(request.POST, instance=bunny)
        else:
            form = self.get_form()
        return self.form_valid(form)


def bunny_create(request):
    if request.method == 'POST':
        form = BunnyForm(request.POST)
        if form.is_valid():
            bunny = Bunny()
            bunny.name = form.cleaned_data['name']
            bunny.sn = form.cleaned_data['sn']
            # bunny.password = make_password(form.cleaned_data['password'])
            # bunny.password = form.cleaned_data['password']
            bunny.connected = False
            bunny.sleep_state = False
            bunny.user = request.user
            bunny.save()
            return HttpResponseRedirect("/vl/bunny")


@login_required
def zstamp(request):
    zstamps = ZStamp.objects.filter(user=request.user)
    context = {
        'zstamps': zstamps,
    }
    return render(request, 'zstamp.html', context)


class ZstampEditView(FormView):
    template_name = 'zstamp_details.html'
    form_class = ZStampEditForm
    success_url = '/vl/zstamp'

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

    def get(self, request, sn):
        zstamp = ZStamp.objects.get(serial=sn)
        form = self.form_class(instance=zstamp)
        context = {
            'form': form
        }
        return render(request, 'bunny_details.html', context)

    def post(self, request, sn):
        zstamp = ZStamp.objects.filter(serial=sn).first()
        if zstamp:
            form = self.form_class(request.POST, instance=zstamp)
        else:
            form = self.get_form()
        return self.form_valid(form)


def plugin(request):
    plugins = Plugin.objects.all()
    context = {
        'plugins': plugins
    }
    return render(request, 'plugin.html', context)
