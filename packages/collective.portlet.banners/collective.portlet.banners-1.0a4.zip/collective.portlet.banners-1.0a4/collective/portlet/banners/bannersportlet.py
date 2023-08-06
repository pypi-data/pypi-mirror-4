from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.component.hooks import getSite
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize.instance import memoize
from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import random
import time
import md5
from collective.portlet.banners import BannerPortletMessageFactory as _


class IBannersPortlet(IPortletDataProvider):
    """
    A portlet to display rotating banner images.
    """

    portlet_title = schema.TextLine(
        title=_(u'Title'),
    )
    
    banner_folder = schema.Choice(
	    title=_(u"Banner Folder"),
        description=_(u"Choose the folder where the banners are located."),
        required=True,
        source=SearchableTextSourceBinder(
            {'is_folderish' : True},
            default_query='path:',
        )
    )

    delay = schema.Int(
        title=_(u'Delay'),
        description=_(u'Enter the banner rotation delay in seconds.'),
        default=5,
        min=1,
        max=100,
    )
    
    fade_speed = schema.Choice(
        title=_(u'Fade Speed'),
        description=_(u'Choose the speed of the fade effect.'),
        vocabulary=SimpleVocabulary.fromItems([
            (u'No fade', 0),
            (u'Fast', 200),
            (u'Medium', 600),
            (u'Slow', 1000),
        ]),
        default=600
    )
    
    width = schema.Int(
        title=_(u'Width'),
        description=_(u'Enter the width of the portlet in pixels. Banner images \
            will be constrained to this width, but this setting does not affect \
            file size.'),
        default=130
    )
    
    order = schema.Choice(
        title=_(u'Order'),
        description=_(u'Choose the order in which the banners will be displayed.'),
        vocabulary=SimpleVocabulary.fromItems([
            (u'Folder Order', u'folder'),
            (u'Random', u'random'),
        ]),
        default=u'folder'
    )

    use_caching = schema.Bool(
        title=_(u"Use Caching"),
        description=_(u"Might not work properly in some invironemnts"),
        default=True)


class Assignment(base.Assignment):
    """
    Assignment for the banners portlet.
    """

    implements(IBannersPortlet)
    use_caching = True

    def __init__(self, portlet_title=u'Banners', banner_folder=u'/', delay=5,
                 fade_speed=600, width=120, order=u'folder', use_caching=True):
        self.portlet_title = portlet_title
        self.banner_folder = banner_folder
        self.delay = delay
        self.fade_speed = fade_speed
        self.width = width
        self.order = order
        self.use_caching = use_caching

    @property
    def title(self):
        """
        Returns the title for the manage portlets screen.
        """
        return "Banners Portlet"


class Renderer(base.Renderer):
    """
    Renderer for the banners portlet.
    """

    render = ViewPageTemplateFile('bannersportlet.pt')
    
    def getTitle(self):
        """
        Returns the portlet title.
        """
        return self.data.portlet_title
    
    def getBanners(self):
        """
        Returns a list of dictionaries containing information about the banners.
        """

        display = 'block'
        for banner_info in self.getBannerInfo():
            width, height = self.getBannerDimensions(banner_info)
            style = 'height:%ipx;display:%s;' % (self.getMaxHeight(), display)
            yield {
                'image': banner_info['image'],
                'url': banner_info['url'],
                'width': width,
                'height': height,
                'style': style,
            }
            display = 'none'
        
    def getBannerDimensions(self, banner_info):
        """
        Returns the width and height of the scaled image.
        """
        height = banner_info['height']
        width = banner_info['width']

        if self.data.width < width:
            scale = float(self.data.width)/float(width)
            width = self.data.width
            height = int(float(height)*scale)

        return (width, height)
    
    def getDelay(self):
        """
        Returns the rotation delay in miliseconds.
        """
        return self.data.delay*1000
        
    def getFadeSpeed(self):
        """
        Returns the fade speed in miliseconds.
        """
        return self.data.fade_speed
    
    @memoize
    def getBannerInfo(self):
        """
        Returns a list of dictionaries containing information about the
        unscaled banners.
        """
        site = getSite()
        catalog_tool = getToolByName(self.context, 'portal_catalog')
        site_path = '/'.join(site.getPhysicalPath())
        brains = catalog_tool.searchResults(
            path='%s%s' % (site_path, self.data.banner_folder),
            sort_on='getObjPositionInParent',
            portal_type='PortletBanner',
        )
        if self.data.order == u'random':
            brains = [b for b in brains]
            random.shuffle(brains)
        results = []
        site_url = site.absolute_url()
        for brain in brains:
            if getattr(self.data, 'use_caching', True):
                info = getattr(brain, 'porletbanner_info', None)
            else:
                obj = brain.getObject()
                info = obj.porletbanner_info()
            if info:
                image = info.get('image', '')
                if not image.startswith('http://') and not image.startswith('https://'):
                    info['image'] = site_url + image
                results.append(info)
            results.append(info)
        return results
    
    @memoize
    def getMaxHeight(self):
        """
        Returns the maximum scaled height of the banner images.
        """
        return max([self.getBannerDimensions(i)[1] for i in self.getBannerInfo()])
        
    @memoize
    def getPortletId(self):
        """
        Returns a unique element ID for the element that contains the banners.
        """
        random_id = md5.new()
        random_id.update(str(time.time()))
        return 'portletbanners-%s' % random_id.hexdigest()


class AddForm(base.AddForm):
    """
    Add form for the banners portlet.
    """
    form_fields = form.Fields(IBannersPortlet)
    form_fields['banner_folder'].custom_widget = UberSelectionWidget
    

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """
    Edit form for the banners portlet.
    """
    form_fields = form.Fields(IBannersPortlet)
    form_fields['banner_folder'].custom_widget = UberSelectionWidget
