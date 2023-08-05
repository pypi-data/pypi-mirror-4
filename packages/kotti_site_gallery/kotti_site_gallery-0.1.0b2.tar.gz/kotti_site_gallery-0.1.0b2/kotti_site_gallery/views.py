import colander
from kotti import DBSession
from kotti.views.edit import ContentSchema
from kotti.views.edit import DocumentSchema
from kotti.views.edit import generic_edit
from kotti.views.edit import generic_add
from kotti.views.view import view_node
from kotti.views.util import ensure_view_selector
from kotti.views.util import template_api
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('kotti_site_gallery')

from kotti_site_gallery.resources import SiteGallery
from kotti_site_gallery.resources import Site


class SiteGallerySchema(ContentSchema):
    pass


class SiteSchema(DocumentSchema):
    url = colander.SchemaNode(colander.String(), title=_("URL"))


@ensure_view_selector
def edit_site_gallery(context, request):
    return generic_edit(context, request, SiteGallerySchema())


def add_site_gallery(context, request):
    return generic_add(context, request, SiteGallerySchema(), SiteGallery,
                       SiteGallery.type_info.title)


@ensure_view_selector
def edit_site(context, request):
    return generic_edit(context, request, SiteSchema())


def add_site(context, request):
    return generic_add(context, request, SiteSchema(), Site,
                       Site.type_info.title)


def view_site_gallery(context, request):
    sites = DBSession.query(Site)\
        .filter(Site.parent_id == context.id)\
        .all()
    return dict(
        api=template_api(context, request),
        sites=sites,
    )


def includeme_edit(config):
    config.add_view(
        edit_site_gallery,
        context=SiteGallery,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        add_site_gallery,
        name=SiteGallery.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        edit_site,
        context=Site,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        add_site,
        name=Site.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )


def includeme_view(config):
    config.add_view(
        view_site_gallery,
        context=SiteGallery,
        name='view',
        permission='view',
        renderer='templates/site-gallery-view.pt',
    )

    config.add_view(
        view_node,
        context=Site,
        name='view',
        permission='view',
        renderer='templates/site-view.pt',
    )


def includeme(config):
    config.add_translation_dirs('kotti_site_gallery:locale/')
    includeme_edit(config)
    includeme_view(config)
