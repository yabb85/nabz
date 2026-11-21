"""
Module to save and play audio message.

Usage:
- long click on bunny to record message.
- simple click to read and delete message.
"""


from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from vl.models import Bunny
from .models import Memo
from json import loads as json_loads
from json import dumps as json_dumps
from xml.etree.ElementTree import Element, SubElement, tostring
from vl.utils import send
from vl.models import Plugin
from pathlib import Path
from time import sleep


# Create your views here.
def index(request):
    memo_confs = Memo.objects.filter(bunny__user=request.user).all()
    context = {
        "memo_confs": memo_confs,
    }
    return render(request, 'memo/index.html', context)


def record(request):
    print('###########################################')
    sn = request.GET.get('sn', None)
    name = request.GET.get('name', None)
    bunny = Bunny.objects.get(sn=sn)
    memo = Memo.objects.filter(bunny=bunny).first()
    if not memo:
        memo = Memo(bunny=bunny)
    if memo.messages:
        messages = json_loads(memo.messages)
        messages.append(name)
    else:
        messages = [name]
    memo.messages = json_dumps(messages)
    memo.last = len(messages) - 1
    memo.save()
    bunny.plugin_active = Plugin.objects.get(name='memo')
    bunny.save()
    action(sn, size=len(messages))
    return HttpResponse('ok')

def one_click(request):
    """
    Read last message selected
    """
    sn = request.GET.get('sn', None)
    bunny = Bunny.objects.get(sn=sn)
    memo = Memo.objects.filter(bunny=bunny).first()
    messages = json_loads(memo.messages)
    # msg = messages.pop()
    msg = messages[memo.last]
    url = request.build_absolute_uri(f'sound/{msg}')
    action(sn, size=len(messages), sound=url)
    # memo.messages = json_dumps(messages)
    # memo.save()
    # if len(messages) == 0:
        # bunny.plugin_active = None
        # bunny.save()
    return HttpResponse('ok')


def double_click(request):
    """
    Remove last message selected
    """
    sn = request.GET.get('sn', None)
    bunny = Bunny.objects.get(sn=sn)
    memo = Memo.objects.filter(bunny=bunny).first()
    messages = json_loads(memo.messages)
    to_be_deleted = messages.pop()
    if not messages:
        memo.last = 0
        bunny.plugin_active = None
        bunny.save()
    elif len(messages) - 1 < memo.last:
        memo.last = len(messages) - 1
    action(sn, size=len(messages))
    memo.messages = json_dumps(messages)
    memo.save()
    Path(to_be_deleted).unlink()
    return HttpResponse('ok')


def ears_move(request):
    """
    Select another message
    """
    sn = request.GET.get('sn', None)
    left = request.GET.get('left', 0)
    if left:
        left = int(left)
    # right = request.GET.get('right', None)
    bunny = Bunny.objects.get(sn=sn)
    memo = Memo.objects.filter(bunny=bunny).first()
    if left > 0 and left < 10:
        memo.last += 1
    elif left > 10 and left < 17:
        memo.last -= 1
    messages = json_loads(memo.messages)
    if memo.last > len(messages) - 1:
        memo.last = len(messages) - 1
    elif memo.last < 0:
        memo.last = 0
    memo.save()
    url = request.build_absolute_uri(f'sound/{messages[memo.last]}')
    action(sn, size=len(messages), sound=url)
    sleep(3)
    # Send after because if send at the sametime of order the ears reset is not executed
    order = Element('order')
    order.set('sn', sn)
    block = SubElement(order, 'block')
    block.text = 'RE\n'
    send(tostring(order))
    return HttpResponse('ok')


def action(sn: str, sound='', size=0):
    print(f'action -> size={size}, sound={sound}')
    order = Element('order')
    order.set('sn', sn)
    ambiant = SubElement(order, 'ambiant')
    if size == 0:
        disable = SubElement(ambiant, 'disable')
        disable.text = '1'
    else:
        mail = SubElement(ambiant, 'mail')
        mail.text = str(min(3, size))
    code = ''
    if sound:
        code += f'MU {sound}\nMW\n'
    if code:
        block = SubElement(order, 'block')
        block.text = code
    print(tostring(order))
    send(tostring(order))


def sound(request, name):
    mp3_path = Path('.')
    mp3_path = mp3_path.joinpath(name)
    try:
        response = FileResponse(open(mp3_path, 'rb'))
        response['content_type'] = 'audio/mpeg'
        return response
    except Exception:  # TODO: define better exception
        raise Http404
