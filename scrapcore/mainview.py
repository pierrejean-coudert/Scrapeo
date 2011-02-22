from django.http import HttpResponse
from django.template import Context, loader

def index(request):
    t = loader.get_template('index.html')
    c = Context({
        "version": "0.0.1",
    })
    return HttpResponse(t.render(c))
    

