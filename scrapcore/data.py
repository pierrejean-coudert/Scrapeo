from django.http import HttpResponse
from django.core import serializers

from models import *
from helpers import *

#------------------------------------------------

def allObjectsOf(model,fields=None):
    all_obj = model.objects.all()
    response = HttpResponse(serializers.serialize("json",all_obj,fields=fields))
    return response

def listSearchEngines(request):
	return allObjectsOf(SearchEngine)	
    
def listAllWebPages(request):
	return allObjectsOf(WebPage)	
    
def listAllQueries(request):
	return allObjectsOf(SearchQuery)	
    
def listAllTags(request):
	return allObjectsOf(Tag,fields=('name',))	

#------------------------------------------------

def listPages(request,tags=''):
    tagNameList = extractTagsStr(tags)
    pages = WebPage.objects.filter(tag__name__in=tagNameList)
    response = HttpResponse(serializers.serialize("json",pages))
    return response


