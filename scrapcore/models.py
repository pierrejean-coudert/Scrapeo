from django.db import models
from helpers import *

class Consts : 
	UNKNOWN = -1

class WebPage(models.Model):
    url      = models.CharField(max_length=300)
    pr       = models.SmallIntegerField(default=Consts.UNKNOWN)
    links_df = models.IntegerField(default=Consts.UNKNOWN)
    links_nf = models.IntegerField(default=Consts.UNKNOWN)
    status   = models.IntegerField(default=Consts.UNKNOWN)
    computed = models.DateTimeField(auto_now=False, default=None)
    
    def __unicode__(self):
        return self.url

class SearchEngine(models.Model):
    name    = models.CharField(max_length=20)
    baseUrl = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name  = models.CharField(max_length=TAGS_MAX_LENGTH)
    pages = models.ManyToManyField(WebPage)
    
    def __unicode__(self):
        return self.name

class SearchQuery(models.Model):
    query     = models.CharField(max_length=500)
    locations = models.ManyToManyField(WebPage)
    execdate  = models.DateTimeField(auto_now=True)
    #engine    = models.ForeignKey(SearchEngine)
    
    def __unicode__(self):
        return str(self.id)+':'+self.query
	
class Proxy(models.Model):
    url        = models.CharField(max_length=500)
    port       = models.SmallIntegerField(default=80)
    lastTested = models.DateTimeField(auto_now=False, default=None)
    
    def __unicode__(self):
        return self.id


