# -*- coding: utf-8 -*-
"""Main Controller"""
from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, tmpl_context, config
from tg.decorators import before_render, cached_property, paginate
from tg.i18n import ugettext as _, lazy_ugettext as l_

try:
    from tg import predicates
except ImportError:
    from repoze.what import predicates

from tgext.pluggable import app_model
from smallpress.model import DBSession, Article, Attachment, Blog
from smallpress.helpers import *
from smallpress.lib.forms import UploadForm, get_article_form, DataGrid, \
    CSSLink, inject_datagrid_resources, SpinnerIcon
from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.datahelpers.fields import AttachedFile
from tgext.pluggable import plug_url, plug_redirect
from webhelpers.html.builder import HTML
from formencode.validators import UnicodeString
from datetime import datetime
from tgext.ajaxforms.ajaxform import formexpose
from tgext.tagging.controllers import TaggingController
from tgext.crud import EasyCrudRestController

try:
    import whoosh
    from whoosh.query import *
    whoosh_enabled = True
except ImportError:
    whoosh_enabled = False

upload_form = UploadForm()
articles_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'edit', 'delete', 'hide', 'publish')),
                                  (l_('Blog'), lambda row:row.blog and row.blog.name),
                                  (l_('Title'), lambda row:HTML.a(row.title,
                                                                  href=plug_url('smallpress', '/view/%s'%row.uid,
                                                                                lazy=True))),
                                  (l_('Tags'), comma_separated_tags),
                                  (l_('Author'), 'author'),
                                  (l_('Publishing'), lambda row:format_published(row) + ', ' + format_date(row))])

attachments_table = DataGrid(fields=[(l_('Actions'), lambda row:link_buttons(row, 'rmattachment')),
                                     (l_('Name'), 'name'),
                                     (l_('Preview'), attachment_preview),
                                     (l_('Url'), lambda row:format_link(row.url))])

def inject_css(*args, **kw):
    CSSLink(link='/_pluggable/smallpress/css/style.css').inject()

class BlogsController(EasyCrudRestController):
    allow_only = predicates.in_group('smallpress')
    title = "Manage Blogs"
    model = Blog

    __form_options__ = {
        '__hide_fields__' : ['uid'],
        '__omit_fields__' : ['articles']
    }

    __table_options__ = {
        '__omit_fields__' : ['uid', 'articles']
    }

class RootController(TGController):
    tagging = TaggingController(model=Article, session=DBSession, allow_edit=None)
    tagging.search = before_render(inject_css)(tagging.search)

    @cached_property
    def blogs(self):
        return BlogsController(DBSession.wrapped_session)

    @expose('genshi:smallpress.templates.index')
    def index(self, blog='', *args, **kw):
        articles = Article.get_published(blog).all()
        tags = app_model.Tagging.tag_cloud_for_set(Article, articles).all()
        return dict(articles=articles, tags=tags, blog=blog)

    @expose('genshi:smallpress.templates.article')
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=index)
    def view(self, article, **kw):
        visible = False

        if article.published and article.publish_date <= datetime.now():
            visible = True
        elif request.identity and article.author == request.identity['user']:
            visible = True
        elif request.identity and 'smallpress' in request.identity['groups']:
            visible = True

        if not visible:
            return redirect(plug_url('smallpress', '/'))

        hooks = config['hooks'].get('smallpress.before_view_article', [])
        for func in hooks:
            func(article, kw)

        return dict(article=article)

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.manage')
    @paginate('articles')
    def manage(self, blog='', *args, **kw):
        articles = Article.get_all(blog)
        return dict(table=articles_table, articles=articles,
                    create_action=self.mount_point+'/new/'+blog)

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.edit')
    def new(self, blog=None, **kw):
        inject_datagrid_resources(attachments_table)

        if 'uid' not in kw:
            if blog:
                blog = DBSession.query(Blog).filter_by(name=blog).first()
            article = Article(author=request.identity['user'], blog=blog and blog)

            hooks = config['hooks'].get('smallpress.before_create_article', [])
            for func in hooks:
                func(article, kw)

            DBSession.add(article)
            DBSession.flush()

            hooks = config['hooks'].get('smallpress.after_create_article', [])
            for func in hooks:
                func(article, kw)
        else:
            article = DBSession.query(Article).get(kw['uid'])

        return plug_redirect('smallpress', '/edit/%s' % article.uid)

    @require(predicates.in_group('smallpress'))
    @expose('genshi:smallpress.templates.edit')
    def edit(self, uid, *args, **kw):
        inject_datagrid_resources(attachments_table)

        article = DBSession.query(Article).get(uid)
        value = {
            'uid':article.uid,
            'title':article.title,
            'description':article.description,
            'tags':comma_separated_tags(article),
            'publish_date':format_date(article),
            'content':article.content
        }

        hooks = config['hooks'].get('smallpress.before_edit_article', [])
        for func in hooks:
            func(article, value)

        return dict(article=article, value=value, blog=article.blog and article.blog.name or '',
                    form=get_article_form(), action=url(self.mount_point+'/save'),
                    upload_form=upload_form, upload_action=url(self.mount_point+'/attach'))

    @require(predicates.in_group('smallpress'))
    @validate(get_article_form(), error_handler=edit)
    @expose()
    def save(self, *args, **kw):
        article = DBSession.query(Article).get(kw['uid'])

        hooks = config['hooks'].get('smallpress.before_save_article', [])
        for func in hooks:
            func(article, kw)

        article.title = kw['title']
        article.description = kw['description']
        article.content = kw['content']
        article.publish_date = datetime.strptime(kw['publish_date'], '%Y-%m-%d %H:%M')
        article.update_date = datetime.now()
        app_model.Tagging.set_tags(article, kw['tags'])

        flash(_('Articles successfully saved'))
        return redirect(self.mount_point+'/manage/'+article.blog_name)

    @require(predicates.in_group('smallpress'))
    @formexpose(upload_form, 'smallpress.templates.attachments')
    def upload_form_show(self, **kw):
        article = DBSession.query(Article).get(kw['article'])
        return dict(value=kw, table=attachments_table, attachments=article.attachments)

    @require(predicates.in_group('smallpress'))
    @validate(upload_form, error_handler=upload_form_show)
    @expose('genshi:smallpress.templates.attachments')
    def attach(self, **kw):
        article = DBSession.query(Article).get(kw['article'])
        attachment = Attachment(name=kw['name'], article=article,
                                content=AttachedFile(kw['file'].file, kw['file'].filename))
        DBSession.add(attachment)
        DBSession.flush()

        return dict(value=dict(article=article.uid),
                    ajaxform=upload_form,
                    ajaxform_id='attachments_form',
                    ajaxform_action=upload_form.action,
                    ajaxform_spinner=SpinnerIcon(),
                    table=attachments_table,
                    attachments=article.attachments)

    @require(predicates.in_group('smallpress'))
    @validate(dict(attachment=SQLAEntityConverter(Attachment)))
    @expose()
    def rmattachment(self, attachment):
        article = attachment.article
        DBSession.delete(attachment)
        flash(_('Attachment successfully removed'))
        return redirect(self.mount_point+'/edit/%s'%article.uid)

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def publish(self, article):
        if not article.content:
            flash(_('Cannot publish an empty article'))
        else:
            article.published=True
            flash(_('Article published'))
        return redirect(self.mount_point+'/manage/'+article.blog_name)

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def hide(self, article):
        article.published=False
        flash(_('Article hidden'))
        return redirect(self.mount_point+'/manage/'+article.blog_name)

    @require(predicates.in_group('smallpress'))
    @validate(dict(article=SQLAEntityConverter(Article)), error_handler=manage)
    @expose()
    def delete(self, article):
        DBSession.delete(article)
        flash(_('Article successfully removed'))
        return redirect(self.mount_point+'/manage/'+article.blog_name)

    @expose('genshi:smallpress.templates.index')
    @validate(dict(text=UnicodeString(not_empty=True)), error_handler=index)
    def search(self, text=None):
        articles = []

        if whoosh_enabled:
            index_path = config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
            ix = whoosh.index.open_dir(index_path)
            with ix.searcher() as searcher:
                query = Or([Term("content", text),
                            Term("title", text),
                            Term("description", text)])
                found = searcher.search(query)
                if len(found):
                    articles = Article.get_published().filter(Article.uid.in_([e['uid'] for e in found])).all()
        else:
            articles = Article.get_published().filter(Article.content.like('%'+text+'%')).all()

        tags = app_model.Tagging.tag_cloud_for_set(Article).all()
        return dict(articles=articles, tags=tags, blog='')
