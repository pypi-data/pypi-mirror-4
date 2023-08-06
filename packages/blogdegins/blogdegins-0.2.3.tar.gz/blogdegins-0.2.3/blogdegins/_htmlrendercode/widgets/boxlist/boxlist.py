# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml

boxlist_data = {
    'myname': 'Blogdegins.',
}


class Boxlist(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        super(Boxlist, self).__init__(fsm=fsm, gconfig=gconfig)

    def render(self, **kw):
        kw.update(**boxlist_data)
        return super(Boxlist, self).render(**kw)


def create_boxlist(parent):
    boxlist = parent.create_gobj(
        None,
        Boxlist,
        parent,
        template='widgets/boxlist/boxlist.mako',
    )
    return boxlist
