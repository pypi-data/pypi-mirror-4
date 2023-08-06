from zope.interface import implements
from Products.Archetypes import atapi
from plone.app.blob.content import ATBlob, ATBlobSchema
from plone.app.blob.interfaces import IATBlobImage
from Products.ATContentTypes.interface import image as atimage
from collective.portlet.banners.config import PROJECTNAME
from collective.portlet.banners.interfaces import IPortletBanner
from collective.portlet.banners import BannerPortletMessageFactory as _
from zope.app.component.hooks import getSite

PortletBannerSchema = \
    ATBlobSchema.copy() + \
    atapi.Schema((
        
        atapi.StringField('url',
            required=False,
            widget = atapi.StringWidget(
                label=_(u'URL'),
                description=_(u'Enter the target URL for the banner.'),
            ),
            validators=('isURL',),
        ),
    
    ))

class PortletBanner(ATBlob):
    """
    A banner that can be displayed in the banner portlet
    """
    
    implements(IPortletBanner, IATBlobImage, atimage.IATImage, atimage.IImageContent)
    
    archetype_name = portal_type = meta_type = "PortletBanner"
    schema = PortletBannerSchema
    
    def porletbanner_info(self):
        """
        Gets information about the portlet banner for cataloging.
        """
        site = getSite()       
        site_path = '/'.join(site.getPhysicalPath())
        image = self.getImage()
        if image.filename:        
            return {
                'image': '/'.join(image.getPhysicalPath())[len(site_path):],
                'url': self.getUrl(),
                'height': image.height,
                'width': image.width,
            }
    
atapi.registerType(PortletBanner, PROJECTNAME)
