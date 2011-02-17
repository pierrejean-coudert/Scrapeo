from gevent import monkey; monkey.patch_all()

from gevent import Greenlet
from gevent.pool import Pool
from gevent.pool import Group
from gevent.queue import Queue
import gevent 
from BeautifulSoup import *
import urllib, urllib2

#---------------------------------------------------------
class BaseBrowser :
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.headers = {
            "User-Agent":'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
        }
    def open(self,url,maxtry=5):
        self.request = urllib2.Request(url)
        for key,value in self.headers.items() :
            self.request.add_header(key,value)
        
        htmlresponse = None
        ntry = 0
        while ntry < maxtry and htmlresponse==None: 
            ntry+=1
            try:
                print ntry,' open failed for ',url
                self.response = self.opener.open(self.request)
                htmlresponse = self.response.read()
            except Exception as e:
                pass
        return htmlresponse
#---------------------------------------------------------
class Job(Greenlet):
    def __init__(self):
        Greenlet.__init__(self)
        self.subjobs = Group()
        self.pool    = None
        
    def _launch(self,subjob,doneNotifier=None):
        subjob.pool = self.pool
        self.subjobs.add(subjob)
        if doneNotifier is not None:
            subjob.link_value(doneNotifier)
        else :
            subjob.link_value(self._endSubjob)
        self.pool.start(subjob)
        return subjob
        
    def _endSubjob(self,subjob):
        None
        
    def joinSubjobs(self):
        while len(self.subjobs)<>0:
            gevent.sleep(1)
            
#---------------------------------------------------------    
class PageRank(Job) :
    def __init__(self, url):
        Job.__init__(self)
        self.browser   = BaseBrowser()
        self.targeturl = url
        self.rank      = None
    def _run(self):
        hsh = self.cek_hash(self.hash_url(self.targeturl))
        gurl = 'http://www.google.com/search?client=navclient-auto&features=Rank:&q=info:%s&ch=%s' % (urllib.quote(self.targeturl), hsh)
        try:
            f = self.browser.open(gurl)
            toprint = '-'*10+ '\n'
            toprint +=  gurl + '\n'
            toprint += f+ '\n'
            toprint += '-'*10+ '\n'
            print toprint
            self.rank = f.strip()[9:]
        except Exception as e:
            self.rank = 'N/A'
        if self.rank == '':
            self.rank = '0'

    def  int_str(self,string, integer, faktor):
        for i in range(len(string)) :
            integer *= faktor
            integer &= 0xFFFFFFFF
            integer += ord(string[i])
        return integer

    def hash_url(self,string):
        c1 = self.int_str(string, 0x1505, 0x21)
        c2 = self.int_str(string, 0, 0x1003F)

        c1 >>= 2
        c1 = ((c1 >> 4) & 0x3FFFFC0) | (c1 & 0x3F)
        c1 = ((c1 >> 4) & 0x3FFC00) | (c1 & 0x3FF)
        c1 = ((c1 >> 4) & 0x3C000) | (c1 & 0x3FFF)

        t1 = (c1 & 0x3C0) << 4
        t1 |= c1 & 0x3C
        t1 = (t1 << 2) | (c2 & 0xF0F)

        t2 = (c1 & 0xFFFFC000) << 4
        t2 |= c1 & 0x3C00
        t2 = (t2 << 0xA) | (c2 & 0xF0F0000)

        return (t1 | t2)

    def cek_hash(self,hash_int):
        hash_str = '%u' % (hash_int)
        bendera = 0
        cek_byte = 0

        i = len(hash_str) - 1
        while i >= 0:
            byte = int(hash_str[i])
            if 1 == (bendera % 2):
                byte *= 2;
                byte = byte / 10 + byte % 10
            cek_byte += byte
            bendera += 1
            i -= 1

        cek_byte %= 10
        if 0 != cek_byte:
            cek_byte = 10 - cek_byte
            if 1 == bendera % 2:
                if 1 == cek_byte % 2:
                    cek_byte += 9
                cek_byte >>= 1

        return '7' + str(cek_byte) + hash_str
#---------------------------------------------------------    
class OutLinks(Job):
    def __init__(self, url):
        Job.__init__(self)
        self.url          = url
        self.dofollowList = []
        self.nofollowList = []
        self.status       = None
        self.browser      = BaseBrowser()

    def _run(self):
        try:
            htmlCode    = self.browser.open(self.url)
            self.status = self.browser.response.getcode()
            scraper     = BeautifulSoup(htmlCode)
        except:
            return
        all_links = scraper.findAll("a")
        for link in all_links:
            try :
                rel = link["rel"]
            except :
                rel=''
            try :
                url = link["href"]
            except :
                url = '' 
            
            try :
                anchor = link.text
            except :
                anchor = '' 
            
            if rel.find('nofollow')==-1:
                self.dofollowList.append((url,anchor))
            else:
                self.nofollowList.append((url,anchor))

#---------------------------------------------------------
class SERPScrapper(Job):
    def __init__(self,query,nbResults,searchBot):
        Job.__init__(self)
        self.resqueue     = Queue()
        self.query        = query
        self.nbResults    = nbResults
        self.searchBot    = searchBot
        self.nbRetResults = 0
    def _run(self):
        while self.nbRetResults < self.nbResults :
            urls = self.searchBot.request(self.query,self.nbRetResults,self.nbResults)
            nbnew = len(urls)
            self.nbRetResults += len(urls)
            if len(urls)==0 : break
            for url in urls:
                self.resqueue.put(url)
    def popResults(self):
        nbsent=0
        while nbsent < self.nbResults :
            yield self.resqueue.get()
            nbsent += 1
#---------------------------------------------------------
class GoogleSearchBot:
    def __init__(self, extension='com'):
        self.extension = extension
        self.baseurl   = 'www.google'
        self.searchcmd = 'search'
        self.browser   = BaseBrowser()
	self.urlPart1  = "http://%s.%s"%(self.baseurl,self.extension)
	
    def _getTrueUrl(self,ggurl):
        trueUrl = None
        if ggurl.startswith('http'):
            trueUrl = ggurl
        elif ggurl.startswith('/url'):
            trueUrl =  urllib.unquote(re.search('(http.*)&sa',ggurl).group(1))
        return trueUrl
        
    def request(self,query,ifirst,nbmax):
        if ifirst >= nbmax :
            return []
        nb = min(100,nbmax)
        #http://www.blueglass.com/blog/google-search-url-parameters-query-string-anatomy/
        url="%s/%s?%s"%(self.urlPart1,self.searchcmd,urllib.urlencode({"q":query,'num':nb,'start':ifirst}))
        htmlCode = self.browser.open(url)
        parser=BeautifulSoup(htmlCode)
        rawresults = parser.findAll('li',{'class':'g'})
        newSerps = []
        for result in rawresults :
            urlelement = result.a
            resurl = self._getTrueUrl(urlelement['href'])
            if resurl :
                newSerps.append(self._getTrueUrl(urlelement['href']))
        return newSerps
#---------------------------------------------------------
class FindPages(Job):
    def __init__(self,query,nbresults=100,searchBot=GoogleSearchBot(),pagenotif=None,prnotif=None,lanotif=None):
        Job.__init__(self)
        self.query           = query
        self.nbresults       = nbresults
        self.searchBot       = searchBot
        self.foundUrls       = {}
        self.pagenotif       = pagenotif
        self.prnotif         = prnotif
        self.lanotif         = lanotif
    
    def set_pr(self,prjob):
        url = prjob.targeturl
        self.foundUrls[url]['PR'] = prjob.rank
        if self.prnotif :
            self.prnotif(prjob)
        
    def set_la(self,lajob):
        url = lajob.url
        self.foundUrls[url]['nbfollow']   = len(lajob.dofollowList)
        self.foundUrls[url]['nbnofollow'] = len(lajob.nofollowList)
        if self.lanotif :
            self.lanotif(lajob)
        
    def _run(self):
        searchbot = self._launch(SERPScrapper(self.query,self.nbresults,self.searchBot))
        for sepage in searchbot.popResults():
            self.foundUrls[sepage]={}
            if self.pagenotif :
                self.pagenotif(sepage)
            self._launch(PageRank(sepage),self.set_pr)
            self._launch(OutLinks(sepage),self.set_la)
        self.joinSubjobs()
        print "JOB FindPages DONE FOR QUERY : ",self.query
#---------------------------------------------------------
class Application :
    def __init__(self,nbworkers=5):
        print nbworkers
        self.pool = Pool(nbworkers)
        self.rootJobs=[] #TODO : remove jobs from here 
        
    def launch(self,newjob,notifier=None):
        self.rootJobs.append(newjob)
        newjob.pool=self.pool
        if notifier is not None:
            newjob.link_value(notifier)
        self.pool.start(newjob)
        return newjob
        
    def findPages(self,footprint,nbresults,googleExtension='com'):
        return self.launch(FindPages(footprint,nbresults,GoogleSearchBot(googleExtension)))
    
