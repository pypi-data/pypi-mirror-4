from Products.Archetypes import atapi
from Products import PatchPloneContent
from archetypes.referencebrowserwidget import widget
# Trigger registration of imageCaption validator
import Products.ImageCaptionValidator

news_image = atapi.ReferenceField('news_image',
               relationship = 'relatesToImage',
               multiValued = False,
               allowed_types=('Image',),
               widget = widget.ReferenceBrowserWidget(
                            image_portal_types=('Image',),
                            allow_search = True,
                            allow_browse = True,
                            show_indexes = False,
                            force_close_on_insert = True,
                            description = '',
                            label='Bruk bilde fra bildearkiv (overstyrer bilde over)',
))

from Products.ATContentTypes.content.newsitem import ATNewsItem

PatchPloneContent.add_validator(ATNewsItem.schema['imageCaption'], 'imageCaption')

PatchPloneContent.content_classes_add_fields((ATNewsItem,), (news_image,))

old_tag = ATNewsItem.tag
# Accessors are defined by now, no?
old_getImage = ATNewsItem.getImage

def getImage(self):
    """Returns a locally stored image or one referenced to."""
    image = self.getNews_image()
    if image: return image
    else: return old_getImage(self)

ATNewsItem.getImage = getImage

def tag(self, **keywords):
    """Custom function that prefers referrenced image over embedded"""
    if not 'title' in keywords:
        keywords['title'] = self.getImageCaption()
    if not 'alt' in keywords:
        keywords['alt'] = self.getImageCaption()
    news_image = self.getNews_image()
    if news_image is not None:
        return news_image.tag(**keywords)
    else:
        return old_tag(self, **keywords)

ATNewsItem.tag = tag
