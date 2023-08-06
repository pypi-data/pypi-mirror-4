from zope import interface, component
from Acquisition import aq_inner

from zope.security.interfaces import Unauthorized

from plone.app.layout.globals.interfaces import IViewView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.quickupload.portlet import quickuploadportlet


JAVASCRIPT = """
  // workaround this MSIE bug :
  // https://dev.plone.org/plone/ticket/10894
  if (jQuery.browser.msie) jQuery("#settings").remove();
  var Browser = {};
  Browser.onUploadComplete = function() {
      window.location.reload();
  }
  loadUploader = function() {
      var ulContainer = jQuery('.QuickUploadView .uploaderContainer');
      ulContainer.each(function(){
          var uploadUrl =  jQuery('.uploadUrl', this).val();
          var uploadData =  jQuery('.uploadData', this).val();
          var UlDiv = jQuery(this);
          jQuery.ajax({
                     type: 'GET',
                     url: uploadUrl,
                     data: uploadData,
                     dataType: 'html',
                     contentType: 'text/html; charset=utf-8',
                     success: function(html) {
                        if (html.indexOf('quick-uploader') != -1) {
                            UlDiv.html(html);
                        }
                     } });
      });
  }
  jQuery(document).ready(loadUploader);
"""


class IUpload(IViewView):
    """ View to upload files
    """

    def __call__():
        """ Renders the view
        """

    def uploadAvailable():
        """ Whether uploading is possible or not
        """


class Upload(quickuploadportlet.Renderer, BrowserView):
    """ View to upload files
    """
    interface.implements(IUpload)
    template = ViewPageTemplateFile('upload.pt')
    data = quickuploadportlet.Assignment()

    def __init__(self, *args):
        BrowserView.__init__(self, *args)
        context = aq_inner(self.context)
        self.view = self
        self.ploneview = context.restrictedTraverse('@@plone')
        self.pm = getToolByName(context, 'portal_membership')

    def uploadAvailable(self):
        """ Whether uploading is possible or not
        """
        return self.available

    def __call__(self):
        if not self.uploadAvailable():
            raise Unauthorized()
        self._clean_session()
        return self.template()

    def javascript(self):
        return JAVASCRIPT
