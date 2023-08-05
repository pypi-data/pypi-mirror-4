# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from tgext.pluggable import PluggableSession, app_model
import tgext.tagging

DBSession = PluggableSession()
DeclarativeBase = declarative_base()

def init_model(app_session):
    DBSession.configure(app_session)

from models import Article, Attachment, Blog

