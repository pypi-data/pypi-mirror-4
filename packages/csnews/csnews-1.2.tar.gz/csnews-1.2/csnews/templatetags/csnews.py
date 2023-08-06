from django import template
from csnews.models import Article

@register.inclusion_tag('news/last_news.html')
def get_last_news():
    return {'last_news': Article.objects.filter(is_public=True).order_by("-published")[:10]}
