from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^scrapeo/', include('scrapeo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    #(r'^/$', 'index'),
    #(r'^scrapeo/searches/', include('scrapeo.scrapcore.views.searches')),
    #(r'^scrapeo/results/', include('scrapeo.scrapcore.views.results')),
    
    #Serve static files : NOT TO BE USED IN PRODUCTION
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static', 'show_indexes': True}),
    (r'^uidev/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static', 'show_indexes': True}),
)

urlpatterns += patterns('scrapeo.scrapcore',
	#(r'^/$','index'),
	
	#=== PRODUCTION / AJAX URLS ===
	(r'^query','ajax_views.findPages'),
	(r'^json/allTags','ajax_views.jsonGetTags'),
	(r'^json/listPages/tag/(?P<tags>[ \w,]*)','ajax_views.jsonListPages'),

    #=== DEV URLS ===
	#actions requests
    (r'^action/findPages/(?P<engineid>[\d]*)/(?P<tags>[ \w,]*)/(?P<query>.*)','actions.findPages'),
    
    # data requests
    (r'^data/listAllTags','data.listAllTags'),
    (r'^data/listPages/tag/(?P<tags>[ \w,]*)','data.listPages'),
    
    # list all objects from a type
    (r'^data/listEngines','data.listSearchEngines'),
    (r'^data/listAllPages','data.listAllWebPages'),
    (r'^data/listAllQueries','data.listAllQueries'),
    )

