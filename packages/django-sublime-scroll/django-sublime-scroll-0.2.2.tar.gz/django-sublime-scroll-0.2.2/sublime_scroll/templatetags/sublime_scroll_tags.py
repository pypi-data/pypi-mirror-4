import os
from subprocess import Popen, PIPE
from PIL import Image
import json
from django.utils.safestring import mark_safe

from django.conf import settings
from ..settings import *

from django import template
register = template.Library()

def urljoin(*args):
    """
    Joins given arguments into a url. Trailing but not leading slashes are
    stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))

def wkhtmltoimage(url, output):
    p = Popen([SUBLIME_SCROLL_WKHTMLTOIMAGE_PATH, url, output], stdout=PIPE, stderr=PIPE)
    errors = p.stdout.read()
    if errors:
        raise Exception(errors)
    #print p.stderr.read()
    return output

@register.inclusion_tag('sublime_scroll/include.html', takes_context=True)
def sublime_scroll(context):
    request = context['request']

    if request.GET.get('screenshot', None) is not None:
        return {'image_path': None}

    path = os.path.join(settings.MEDIA_ROOT, 'sublime-scroll' + request.path)
    capture_path = path + 'capture.png'
    resized_path = path + 'small.png'

    try:
        os.makedirs(path)
    except OSError:
        pass
    wkhtmltoimage(request.build_absolute_uri() + '?screenshot=true', capture_path)

    basewidth = SUBLIME_SCROLL_SETTINGS['scroll_width']
    img = Image.open(open(capture_path, 'rb'))
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    img.save(resized_path, 'PNG')

    context['image_path'] = urljoin(settings.MEDIA_URL, 'sublime-scroll', request.path, "small.png")
    context['settings'] = mark_safe(json.dumps(SUBLIME_SCROLL_SETTINGS))

    return context