import sys
import tg
from tg.i18n import lazy_ugettext as l_
from tgext.ajaxforms import ajaxloaded
from tgext.pluggable import plug_url

class SpinnerIcon(object):
    @property
    def link(self):
        return tg.url('/_pluggable/smallpress/images/spinner.gif')

if tg.config.get('prefer_toscawidgets2', False):
    from tw2.core import CSSLink, Required
    from tw2.forms import DataGrid
    from tw2.forms import ListForm, TextField, TextArea, HiddenField, FileField, SubmitButton
    from formencode.validators import UnicodeString, FieldStorageUploadConverter

    def inject_datagrid_resources(dg):
        resources = [r.req() for r in dg.resources]
        for r in resources:
            r.prepare()

    class ArticleForm(ListForm):
        uid = HiddenField()
        title = TextField(label='Title', validator=UnicodeString(not_empty=True, outputEncoding=None))
        description = TextField(label='Description', validator=UnicodeString(outputEncoding=None),
                                placeholder=l_('If empty will be extracted from the content'))
        tags = TextField(label='Tags', validator=UnicodeString(outputEncoding=None),
                         placeholder=l_('tags, comma separated'))
        content = TextArea(label=None, key='content', name='content', id="article_content",
                           validator=UnicodeString(not_empty=True, outputEncoding=None))
        publish_date = TextField(label='Publish Date')

    @ajaxloaded
    class UploadForm(ListForm):
        article = HiddenField()
        name = TextField(label='Name', validator=UnicodeString(not_empty=True, outputEncoding=None))
        file = FileField(label='File', validator=FieldStorageUploadConverter(not_empty=True))

        action = plug_url('smallpress', '/attach', lazy=True)
        ajaxurl = plug_url('smallpress', '/upload_form_show', lazy=True)

        submit = SubmitButton(value='Attach')

    class SearchForm(ListForm):
        text = TextField(label=None, validator=UnicodeString(not_empty=True, outputEncoding=None),
                         placeholder=l_('Search...'))

        submit = SubmitButton(value='Search')

else:
    from tw.api import CSSLink
    from tw.forms import ListForm, TextField, TextArea, HiddenField, FileField
    from tw.forms import DataGrid
    from tw.core import WidgetsList
    from tw.forms.validators import UnicodeString, FieldStorageUploadConverter

    def inject_datagrid_resources(dg):
        dg.register_resources()

    class ArticleForm(ListForm):
        class fields(WidgetsList):
            uid = HiddenField()
            title = TextField(label_text='Title', validator=UnicodeString(not_empty=True))
            description = TextField(label_text='Description', validator=UnicodeString(),
                                    attrs=dict(placeholder=l_('If empty will be extracted from the content')))
            tags = TextField(label_text='Tags', validator=UnicodeString(),
                             attrs=dict(placeholder=l_('tags, comma separated')))
            content = TextArea(suppress_label=True, validator=UnicodeString(not_empty=True),
                               attrs=dict(id='article_content'))
            publish_date = TextField(label_text='Publish Date')

    @ajaxloaded
    class UploadForm(ListForm):
        class fields(WidgetsList):
            article = HiddenField()
            name = TextField(label_text='Name', validator=UnicodeString(not_empty=True))
            file = FileField(label_text='File', validator=FieldStorageUploadConverter(not_empty=True))

        action = plug_url('smallpress', '/attach', lazy=True)
        ajaxurl = plug_url('smallpress', '/upload_form_show', lazy=True)
        submit_text = 'Attach'

    class SearchForm(ListForm):
        class fields(WidgetsList):
            text = TextField(suppress_label=True, validator=UnicodeString(not_empty=True),
                             attrs=dict(placeholder=l_('Search...')))

        submit_text = 'Search'

def get_article_form():
    config = tg.config['_smallpress']

    article_form = config.get('form_instance')
    if not article_form:
        form_path = config.get('form', 'smallpress.lib.forms.ArticleForm')
        module, form_name = form_path.rsplit('.', 1)
        module = __import__(module, fromlist=form_name)
        form_class = getattr(module, form_name)
        article_form = config['form_instance'] = form_class()

    return article_form
