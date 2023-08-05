from kotti.resources import Content
from kotti.resources import Document
from kotti.resources import IContent
from kotti.resources import IDefaultWorkflow
from kotti.resources import IDocument
from kotti.resources import Image
from pyramid.i18n import TranslationStringFactory
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from zope.interface import implements

_ = TranslationStringFactory('kotti_site_gallery')


class SiteGallery(Content):

    __tablename__ = 'site_galleries'
    __mapper_args__ = dict(polymorphic_identity='site_gallery')

    implements(IContent, IDefaultWorkflow)

    id = Column('id', Integer, ForeignKey('contents.id'), primary_key=True)

    type_info = Content.type_info.copy(
        name=u'SiteGallery',
        title=_(u"Site gallery"),
        add_view=u'add_site_gallery',
        addable_to=[u'Document'],
    )

    def __init__(self, **kwargs):

        super(SiteGallery, self).__init__(**kwargs)


class Site(Document):

    implements(IDocument, IDefaultWorkflow)

    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    url = Column(String(100))

    type_info = Document.type_info.copy(
        name=u'Site',
        title=_(u'Site'),
        add_view=u'add_site',
        addable_to=[u'SiteGallery'],
    )

    def get_icon(self):
        """Get icon child image."""

        for picture in self.get_pictures():
            return picture

        return None

    def get_pictures(self):

        pictures = []

        for child in self.keys():
            if self[child].type_info.name == Image.type_info.name:
                pictures.append(self[child])

        return pictures

    def __init__(self, url=None, **kwargs):

        super(Site, self).__init__(in_navigation=False, **kwargs)
        self.url = url
