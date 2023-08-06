import monsieur
import simplejson
import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

is_superuser = user_passes_test(lambda u: u.is_superuser)

@is_superuser
def home(request):
    return render(request, 'monsieur/home.html')

@is_superuser
def json(request, name=None, granularity='minute'):
    attrs = dict(request.GET.items())
    q = monsieur.Q.events(name).filter(attrs).granularity(granularity)
    return JsonResponse(q.eval())

@is_superuser
def attrs(request, prefix, name):
    attrs = dict(request.GET.items())
    q = monsieur.Q.tag(name) if prefix == 'tag' else monsieur.Q.events(name)
    q = q.filter(attrs)
    return JsonResponse(q.attrs())

@is_superuser
def names(request, tag):
    q = monsieur.Q.tag(tag)
    return JsonResponse(q.names())

class JsonResponse(HttpResponse):
    def __init__(self, obj, status=200):
        def default(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            else:
                return None

        data = simplejson.dumps(obj, default=default)
        super(JsonResponse, self).__init__(data, status=status, content_type='text/json')
