from tg import request, config

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation
from sqlalchemy.orm.interfaces import MapperExtension

import os
from datetime import datetime
from smallpress.model import DeclarativeBase, DBSession
from tgext.pluggable import app_model, primary_key
from tgext.datahelpers.fields import Attachment as DataHelpersAttachment
from tgext.pluggable import call_partial

import mimetypes
mimetypes.init()

try:
    import whoosh
    import whoosh.index
    import whoosh.fields
    WHOOSH_SCHEMA = whoosh.fields.Schema(uid=whoosh.fields.ID(stored=True),
                                         title=whoosh.fields.TEXT(stored=True),
                                         description=whoosh.fields.TEXT,
                                         content=whoosh.fields.TEXT)
    whoosh_enabled = True
except ImportError:
    whoosh_enabled = False

try:
    from sqlalchemy import event
    sqla_events = True
except ImportError:
    sqla_events = False

class Blog(DeclarativeBase):
    __tablename__ = 'smallpress_blogs'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(100), nullable=False, default=u"Untitled", index=True)

class Article(DeclarativeBase):
    if not sqla_events:
        class Hooks(MapperExtension):
            def before_delete(self, mapper, connection, instance):
                Article.before_delete(mapper, connection, instance)
        __mapper_args__ = {'extension': Hooks()}

    __tablename__ = 'smallpress_articles'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(Unicode(150), nullable=False, default=u"Untitled", index=True)
    published = Column(Integer, nullable=False, default=0, index=True)
    private = Column(Integer, nullable=False, default=0)

    author_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    author = relation(app_model.User, backref=backref('articles'))

    blog_id = Column(Integer, ForeignKey(primary_key(Blog)), nullable=True, index=True)
    blog = relation(Blog, backref=backref('articles'), lazy='joined')

    publish_date = Column(DateTime, nullable=False, default=datetime.now)
    update_date = Column(DateTime, nullable=False, default=datetime.now)
    description = Column(Unicode(150), nullable=False, default=u'Empty article, edit or delete this')
    content = Column(Unicode(32000), nullable=False, default=u'')

    def refresh_whoosh(self, action=0):
        index_path = config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
        ix = whoosh.index.open_dir(index_path)
        writer = ix.writer()

        if action == 1:
            writer.add_document(uid=unicode(self.uid), title=self.title,
                                content=self.content,
                                description=self.description)
        elif action == -1:
            writer.delete_by_term('uid', unicode(self.uid))
        else:
            writer.update_document(uid=unicode(self.uid), title=self.title,
                                   content=self.content,
                                   description=self.description)
        writer.commit()

    @staticmethod
    def after_update(mapper, connection, obj):
        obj.refresh_whoosh(0)

    @staticmethod
    def after_insert(mapper, connection, obj):
        obj.refresh_whoosh(1)

    @staticmethod
    def whoosh_before_delete(mapper, connection, obj):
        obj.refresh_whoosh(-1)

    @staticmethod
    def before_delete(mapper, connection, obj):
        if whoosh_enabled:
            Article.whoosh_before_delete(mapper, connection, obj)

        DBSession.query(app_model.Tagging).filter(app_model.Tagging.taggable_type == 'Article')\
                                          .filter(app_model.Tagging.taggable_id == obj.uid).delete()

    @staticmethod
    def get_published(blog=None):
        now = datetime.now()
        articles = DBSession.query(Article).filter_by(published=True)\
                                           .filter(Article.publish_date<=now)

        if blog:
            try:
                blog = blog.name
            except:
                pass
            articles = articles.join(Blog).filter(Blog.name==blog)

        articles = articles.order_by(Article.publish_date.desc())
        return articles

    @staticmethod
    def get_all(blog=None):
        articles = DBSession.query(Article)
        if blog:
            try:
                blog = blog.name
            except:
                pass
            articles = articles.join(Blog).filter(Blog.name==blog)
        articles = articles.order_by(Article.publish_date.desc())
        return articles

    @property
    def blog_name(self):
        blog = self.blog
        if blog:
            return blog.name
        else:
            return ''

    def tagging_display(self):
        return call_partial('smallpress.partials:article_preview', article=self)

    def is_owner(self, identity):
        if not identity:
            return False

        return identity['user'] == self.author

if whoosh_enabled and sqla_events:
    event.listen(Article, 'after_update', Article.after_update)
    event.listen(Article, 'after_insert', Article.after_insert)

if sqla_events:
    event.listen(Article, 'before_delete', Article.before_delete)

class Attachment(DeclarativeBase):
    if not sqla_events:
        class Hooks(MapperExtension):
            def before_delete(self, mapper, connection, instance):
                Attachment.delete_file(mapper, connection, instance)
        __mapper_args__ = {'extension': Hooks()}

    __tablename__ = 'smallpress_attachments'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(16), nullable=False)
    content = Column(DataHelpersAttachment)

    article_id = Column(Integer, ForeignKey(Article.uid))
    article = relation(Article, backref=backref('attachments', cascade='all, delete-orphan'))

    @staticmethod
    def delete_file(mapper, connection, obj):
        try:
            os.unlink(obj.content.local_path)
        except:
            pass

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.content.local_path, False)[0]

    @property
    def url(self):
        return self.content.url

if sqla_events:
    event.listen(Attachment, 'before_delete', Attachment.delete_file)
