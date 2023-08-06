# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml

content_data = {
    'myname': 'Blogdegins.',
}


class Content(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        super(Content, self).__init__(fsm=fsm, gconfig=gconfig)

    def render(self, **kw):
        kw.update(**content_data)
        return super(Content, self).render(**kw)


def create_content(parent):
    content = parent.create_gobj(
        None,
        Content,
        parent,
        template='content.mako',
    )
    from widgets.boxlist.boxlist import create_boxlist
    create_boxlist(content)
    return content
