from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.core.files.storage import default_storage
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
import re


SIZE_RE = re.compile(r'^(\d+),(\d+)$')


def resize(request, path):
    thumbnail_opts = {}
    if 'size' in request.GET:
        if SIZE_RE.match(request.GET['size']):
            thumbnail_opts['size'] = map(int, request.GET['size'].split(','))
            if 'crop' in request.GET:
                thumbnail_opts['crop'] = request.GET['crop']
        else:
            return HttpResponseBadRequest(u'Size must be expressed in the format "size=[integer],[integer]"')
    else:
        return HttpResponsePermanentRedirect(default_storage.url(path))
    try:
        thumbnailer = get_thumbnailer(default_storage, path)
        thumbnail = thumbnailer.get_thumbnail(thumbnail_opts)
        return HttpResponsePermanentRedirect(thumbnail.url)
    except IOError:
        return HttpResponseNotFound(u'File not found.')
    except InvalidImageFormatError:
        return HttpResponseBadRequest(u'File is not an image.')
