from django.http import HttpResponse
from django.core import serializers
from django import forms
from django.db import models

from models import *
from helpers import *
import actions 

#------------------------------------------------
    
def jsonGetTags(request):
    return HttpResponse('[%s]'%(','.join(['"%s"'%tag.name for tag in Tag.objects.all()])) )

#------------------------------------------------

class listPagesForm(forms.Form):
    tags = forms.CharField()

def jsonListPages(request,tags):
    if request.is_ajax() and request.method=='GET':
        taglist = tags.split(',')
        pages = WebPage.objects.all();
        for tag in taglist :
            pages = pages.filter(tag__name__exact=tag)
            
        jsonResult = '[%s]'%','.join(['["%s","%s","%s","%s"]'%(
            page.pr, page.links_df,page.links_nf,page.url) for page in pages])
        response = HttpResponse(jsonResult)
        return response
    # Prevent non XHR calls
    else:
        return HttpResponse('only ajax pliz',status=400)

#------------------------------------------------

class findPagesForm(forms.Form):
    search_query = forms.CharField()
    tags_query = forms.CharField()

def findPages(request):
    if request.is_ajax() and request.method=='POST':
        formData = findPagesForm(request.POST)
        if formData.is_valid():
            actions.findPages(
                request,
                query=formData.cleaned_data['search_query'],
                tags=formData.cleaned_data['tags_query']
                )
            return HttpResponse('Query received')
        else:
            return HttpResponse('Invalid')
    # Prevent non XHR calls
    else:
        return HttpResponse('only ajax pliz',status=400)

#------------------------------------------------

