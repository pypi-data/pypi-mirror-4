from django.contrib.syndication.views import Feed
from csnews.models import Article
from django.contrib.comments.models import Comment

class LatestNews(Feed):
    title = 'Albisteak'
    link = '/albisteak/'
    description = 'Albisteak'
    
    title_template = 'feeds/rss_title.html'
    description_template = 'feeds/rss_description.html'

    def items(self):
        return Article.objects.filter(is_public=True).order_by('-published')[:20]

    def item_pubdate(self,item):
        return item.published
        
    def item_link(self,item):
        return u'/albisteak/%s?utm_source=rss_link&utm_medium=rss&utm_campaign=rss_feed' % (item.slug)
        
    class LatestComments(Feed):
    title = 'Iruzkinak'
    link = '/albisteak/feed-iruzkinak'
    description = 'Iruzkinak'
    
    title_template = 'feeds/rss_title.html'
    description_template = 'feeds/rss_description.html'

    def items(self):
        return Comment.objects.filter(is_public=True).order_by('-submit_date')[:20]

    def item_pubdate(self,item):
        return item.submit_date
        
    def item_link(self,item):
        return u'%s?utm_source=rss_link&utm_medium=rss&utm_campaign=rss_feed' % (item.content_object.get_absolute_url)
