from Acquisition import Implicit, aq_parent
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.Archetypes.Storage import AttributeStorage

from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator

from zope.interface import implements

class ImageCaptionValidator(Implicit):
    " "

    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kw):
        schema = instance.Schema()
        value = value.strip()
        # news_image is a part of Products.EnhancedNewsItemImage
        data = None
        try:
            data = instance.aq_base.getImage()
        except AttributeError: pass
        if not data:
            data = instance.REQUEST.form.get('image_file')
        image_data = data and True
        data = instance.REQUEST.form.get('news_image', '')
        news_image_data = data and True
        if image_data or news_image_data:
            if not value: return "Missing image caption"
        return True

validation.register(ImageCaptionValidator('imageCaption',
    title='Image caption validator',
    description="""Validates that image caption is set,
if image has been set.""")
)
