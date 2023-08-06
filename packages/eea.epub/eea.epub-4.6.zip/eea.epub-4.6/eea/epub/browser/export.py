""" Export as epub
"""

from App.Common import package_home
from Products.Five import BrowserView
from StringIO import StringIO
from zipfile import ZipFile
from zope.app.pagetemplate import ViewPageTemplateFile
import os.path

def replace(filePath, variables):
    """ Replaces content from a file with given variables
    """
    filePath = os.path.join(package_home(globals()), 'static', filePath)
    f = open(filePath)
    content = f.read()
    f.close()
    return content % variables

class ExportView(BrowserView):
    """ ExportView Browserview
    """
    template = ViewPageTemplateFile('epub.pt')

    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/xml+epub')
        response.setHeader(
                'Content-Disposition', 'attachment; filename=%s.epub' %
                                                                self.context.id)

        templateOutput = self.template(self)
        # This encoding circus was required for including context.getText() 
        # in the template
        templateOutput = templateOutput.decode('utf-8')
        templateOutput = templateOutput.encode('utf-8')
        inMemoryOutputFile = StringIO()

        variables = {
            'TITLE': self.context.Title(),
            'IDENTIFIER': self.context.absolute_url()
        }

        zipFile = ZipFile(inMemoryOutputFile, 'w')
        zipFile.writestr('mimetype', 'application/epub+zip')
        zipFile.writestr('META-INF/container.xml', replace(
                                        'META-INF/container.xml', {}))

        zipFile.writestr('OEBPS/content.xhtml', templateOutput)
        zipFile.writestr('OEBPS/content.opf', replace(
                                            'OEBPS/content.opf', variables))
        zipFile.writestr('OEBPS/toc.ncx', replace('OEBPS/toc.ncx', variables))
        zipFile.close()

        inMemoryOutputFile.seek(0)
        return inMemoryOutputFile.read()
