# coding: utf-8

# Python imports
import os
import tempfile
import zipfile
#import types

from Products.Five import BrowserView
from tempfile import TemporaryFile


class Exporter(BrowserView):
    
    def __init__(self, context, request):
        super(Exporter, self).__init__(context, request)

    
    def __call__(self,REQUEST):
        '''Returns the file (with the 'scaled' images
        '''
        imagesize = self.request.get('imagesize', 'large')  #Using large if nothing is specified
        
    
        # Write ZIP archive
        zip_filename = tempfile.mktemp()
        ZIP = zipfile.ZipFile(zip_filename, 'w')

        for obj in self.context.getFolderContents():
            obj = obj.getObject()
            #print obj.format

            if obj.portal_type == 'Image':
                # export one scale
                #unfortunately, I dont know the format.
                #Guessing on jpg
                full_image_name = obj.getId() + '.jpg'
                img = obj.Schema().getField('image').getScale(obj,scale=imagesize)
                ZIP.writestr(self.context.getId() + '/' + full_image_name, str(img.data))
        
        ZIP.close()
        data = file(zip_filename).read()
        os.unlink(zip_filename) 
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/zip')
        R.setHeader('content-length', len(data))
        R.setHeader('content-disposition', 'attachment; filename="%s.zip"' % self.context.getId())
        return R.write(data) 




    
    
    

