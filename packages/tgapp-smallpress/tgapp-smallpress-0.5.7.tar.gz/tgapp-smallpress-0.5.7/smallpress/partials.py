from tg import expose, request
from smallpress.model import Article
from tgext.pluggable import plug_url, primary_key, app_model
from tgext.tagging.widgets import TagCloud
from smallpress.lib.forms import SearchForm

search_form = SearchForm()

WEEK_EXPIRE = 3600*24*7

@expose('genshi:smallpress.templates.articles')
def articles(articles=None, blog=None):
    if articles is None:
        articles=Article.get_published(blog)
    return dict(articles=articles)

@expose('genshi:smallpress.templates.article_preview')
def article_preview(article):
    user = 'anonymous'
    if request.identity:
        user = getattr(request.identity['user'], primary_key(app_model.User).key)
    return dict(article=article, tg_cache=dict(key='%s-%s-%s' % (article.uid, user,
                                                                 article.update_date.strftime('%Y-%m-%d_%H:%M:%S')),
                                               expire=WEEK_EXPIRE,
                                               type='memory'))

@expose('genshi:smallpress.templates.tagcloud')
def tagcloud(tags=None):
    tagcloud=TagCloud(tagging_url=plug_url('smallpress', '/tagging'))
    if tags is None:
        tags = app_model.Tagging.tag_cloud_for_set(Article).all()
    return dict(tagcloud=tagcloud, tags=tags)

@expose('genshi:smallpress.templates.search')
def search():
    return dict(form=search_form, action=plug_url('smallpress', '/search'),
                tg_cache=dict(key='search', expire=None, type='memory'))

@expose('genshi:smallpress.templates.articles_excerpts')
def excerpts(articles=None, blog=None):
    if articles is None:
        articles=Article.get_published(blog)
    return dict(articles=articles)

@expose('genshi:smallpress.templates.excerpt')
def excerpt(article):
    return article_preview(article)
