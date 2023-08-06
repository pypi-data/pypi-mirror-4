try:
    from Products.ATContentTypes.interface.image import IATImage
except ImportError:
    from Products.ATContentTypes.interfaces import IATImage
from zope.component import adapts
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import public as atapi
try:
    from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
except ImportError:
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.interface import implements
from Products.validation import V_REQUIRED


class ReferenceField(ExtensionField, atapi.ReferenceField):
    pass


class StringField(ExtensionField, atapi.StringField):
    pass


class ExtendedTextField(ExtensionField, atapi.TextField):
    pass


class ExtendedImageField(ExtensionField, atapi.ImageField):
    pass


class GalleryImageExtender(object):
    adapts(IATImage)
    implements(ISchemaExtender)

    fields = [
        ReferenceField('linksTo',
            relationship="KnowsAbout",
            multiValued=False,
            allowed_types=(),
            required=False,
            widget=ReferenceBrowserWidget(
                label=u'Links to',
                description=u"Clicking image goes to this URL. "
                            u"The 'Enable bodytext' must be enabled for your "
                            u"Gallery in order for this to work properly"
            )
        ),
        ExtendedTextField('text',
            required=False,
            searchable=True,
            primary=False,
            storage=atapi.AnnotationStorage(migrate=True),
            validators=('isTidyHtmlWithCleanup',),
            widget=atapi.RichWidget(
                description='Use in some galleries to provide WYSIWYG editor '
                            'for description of images. If not provided, it will '
                            'default to a combination of title and description field '
                            'values. '
                            u"The 'Enable bodytext' must be enabled for your "
                            u"Gallery in order for this to work properly",
                label=u'Text',
                rows=25
            )
        ),
        ExtendedImageField("thumbnailImage",
            required=False,
            storage=atapi.AnnotationStorage(migrate=True),
            languageIndependent=True,
            sizes={'large': (768, 768), 'preview': (400, 400),
                   'mini': (200, 200), 'thumb': (128, 128),
                   'tile': (64, 64), 'icon': (32, 32), 'listing': (16, 16)},
            validators=(('isNonEmptyFile', V_REQUIRED),),
            widget=atapi.ImageWidget(
                description=u"Use this instead of the normal thumbnail",
                label=u"Custom Thumbnail image",
                show_content_type=False
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if self.context.portal_type == 'GalleryImage':
            return self.fields
        return []
