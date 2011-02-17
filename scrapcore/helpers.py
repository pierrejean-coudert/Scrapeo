from django.http import HttpResponse
from django.core import serializers

#constants
TAGS_MAX_LENGTH = 50

#format strings
TAGS_FORMAT = '%%.%ds'%TAGS_MAX_LENGTH

def extractTagsStr(rawtaglist):
    return [TAGS_FORMAT%tg.strip() for tg in rawtaglist.split(',')]
    

def jsonAllObjectsOf(model,fields=None):
    all_obj = model.objects.all()
    response = HttpResponse(serializers.serialize("json",all_obj,fields=fields))
    return response

