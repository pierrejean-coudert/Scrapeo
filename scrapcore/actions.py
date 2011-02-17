from django.http import HttpResponse
from scrapcore import core
from scrapcore.models import *
from datetime import datetime

class FindPagesCallBacks :
    def __init__(self, searchQuery,tags):
        self.searchQuery = searchQuery
        self.taglist = [self.gcTag(tg) for tg in extractTagsStr(tags)]
    
    def gcTag(self,strtag):
        try:
            result = Tag.objects.get(name__exact=strtag)
        except Tag.DoesNotExist :
            result = Tag(name=strtag)
            result.save()
        return result
      
        
    def gcWebPage(self,url):
        try:
            result = WebPage.objects.get(url__exact=url)
        except WebPage.DoesNotExist :
            result = WebPage(url=url)
        result.computed = datetime.now()
        return result
        
    def pr_update(self,prjob):
        wp = self.gcWebPage(prjob.targeturl)
        try:
            wp.pr = int(prjob.rank)
        except ValueError :
            wp.pr = Consts.UNKNOWN
        wp.save()
    
    def la_update(self,la_job):
        wp = self.gcWebPage(la_job.url)
        wp.links_df = len(la_job.dofollowList)
        wp.links_nf = len(la_job.nofollowList)
        if la_job.status :
            wp.status   = la_job.status
        else:
            wp.status   = -1
        wp.save()
    
    def page_update(self,url):
        wp = self.gcWebPage(url)
        wp.save()
        self.searchQuery.locations.add(wp)
        self.searchQuery.save()
        for tag in self.taglist:
            tag.pages.add(wp)
            tag.save()

def findPages(request,query='',engineid='', nbresults=5, tags=''):
    searchQuery = SearchQuery(query=query)
    searchQuery.save()
    callBacks = FindPagesCallBacks(searchQuery,tags)
    job = core.FindPages(
        query,
        nbresults = nbresults,
        searchBot = core.GoogleSearchBot(),
        pagenotif = callBacks.page_update,
        prnotif = callBacks.pr_update,
        lanotif = callBacks.la_update
        )
    core.application.launch(job)
    response = "Find pages<br>\n"
    response += "engineid = %s<br>\n"%engineid
    response += "<br>\n"
    response += "query    = %s<br>\n"%query
    response += "<br>\n"
    response += "tags    = %s<br>\n"%tags
    response += "\n"
    return HttpResponse(response)
