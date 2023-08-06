from geoprisma_config.models import Widget
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
import simplejson

def index(request):
    return render_to_response('geoprisma_config/base.html')

def service(request):
    return render_to_response('admin/base2.html', {'title': 'GeoPrisma Admin GUI: Services'})

def widgets(request):
    if True or request.method == 'GET' and request.GET.has_key('request') and request.GET['request'] == "getWidgetsList":

        json = []
        try:
            widgets = Widget.objects.all()
            for widgetModel in widgets:
                widget = {'name': widgetModel.name, 
                          'id': widgetModel.id,
                          'type': widgetModel.type}
                json.append(widget)
        except ObjectDoesNotExist:
            pass

        json.append({'name': '-- GP-Separator --',
                     'id': '__separator__',
                     'type': None})
        json.append({'name': '-- GP-EditFeature --',
                     'id': '__editfeature__',
                     'type': None})
        return HttpResponse(simplejson.dumps(json))
            
    else:
        raise Http404
