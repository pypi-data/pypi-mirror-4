from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class GalleryInfo(ViewletBase):
    render = ViewPageTemplateFile('galleryinfo.pt')
    #need to find a way to check if there are images
    images = 0
