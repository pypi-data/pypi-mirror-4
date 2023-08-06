from django.contrib import sitemaps
import datetime
from djig.models import Articleclass 

class DjigSitemap(sitemaps.Sitemap):    
    changefreq = "daily"    
    priority   = 0.5    
    
    def items(self):        
        return Article.objects.all()    
    
    def lastmod(self, obj):
        return obj.created
