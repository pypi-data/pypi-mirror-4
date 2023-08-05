# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-smallpress."""

from tg import url, request
from tg.i18n import ugettext as _
from webhelpers import date, feedgenerator, html, number, misc, text
from smallpress import model
from tgext.pluggable import app_model

def bold(text):
    return html.literal('<strong>%s</strong>' % text)

def link_buttons(entity, *buttons):
    btns_html = '<div class="smallpress_buttons">'
    for btn in buttons:
        if btn == 'publish' and entity.published:
            continue
        elif btn == 'hide' and not entity.published:
            continue
        elif btn in ('delete', 'rmattachment'):
            btns_html += '''\
    <a href="%(baseurl)s/%(btn)s/%(entity)s" onclick="return confirm('%(confirm_message)s')">
        <img src="/_pluggable/smallpress/buttons/%(btn)s.png"/>
    </a>''' % dict(baseurl=request.controller_state.controller.mount_point,
                   confirm_message=_('Really delete this?'), btn=btn,
                   entity=entity.uid)
        else:
            btns_html += '''\
    <a href="%(baseurl)s/%(btn)s/%(entity)s">
        <img src="/_pluggable/smallpress/buttons/%(btn)s.png"/>
    </a>''' % dict(baseurl=request.controller_state.controller.mount_point, btn=btn, entity=entity.uid)
    btns_html += '</div>'

    return html.literal(btns_html)

def comma_separated_tags(entity):
    return ', '.join((t[0] for t in app_model.Tagging.tag_cloud_for_object(entity)))

def format_published(entity):
    if entity.published:
        return html.builder.HTML.strong('Published')
    else:
        return 'Draft'

def format_date(entity):
    return entity.publish_date.strftime('%Y-%m-%d %H:%M')

def format_link(url):
    return html.builder.HTML.a(url, href=url, target='_blank')

def attachment_preview(attachment):
    attachment_mime_type = attachment.mimetype
    if attachment_mime_type and attachment_mime_type.startswith('image'):
        preview_url = attachment.url
    else:
        preview_url = "/_pluggable/smallpress/images/unknown.png"
    return html.literal('<img src="%s" class="smallpress_attachment_minipreview"/>' % preview_url)