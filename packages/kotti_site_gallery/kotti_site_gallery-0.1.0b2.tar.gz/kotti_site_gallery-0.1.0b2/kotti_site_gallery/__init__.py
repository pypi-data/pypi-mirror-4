from fanstatic import Library
from fanstatic import Resource
from kotti.resources import Image
import kotti.static as ks


lib_kotti_site_gallery = Library('kotti_site_gallery', 'static')
view_css = Resource(lib_kotti_site_gallery, "kotti_site_gallery.css",
                    depends=[ks.view_css])


def kotti_configure(settings):
    settings['pyramid.includes'] += ' kotti_site_gallery.views.includeme'
    settings['pyramid.includes'] += ' kotti_site_gallery.includeme'
    settings['kotti.available_types'] += (
        ' kotti_site_gallery.resources.SiteGallery')
    settings['kotti.available_types'] += ' kotti_site_gallery.resources.Site'
    Image.type_info.addable_to.append(u'Site')


def includeme(config):
    ks.view_needed.add(view_css)
