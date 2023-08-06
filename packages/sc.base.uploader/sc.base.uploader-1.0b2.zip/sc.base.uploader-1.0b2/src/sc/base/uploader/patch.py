# -*- coding:utf-8 -*-
from collective.zipfiletransport.utilities.utils import ZipFileTransportUtility
from os import close
from Products.ATContentTypes import interfaces
from zipfile import ZipFile, ZIP_DEFLATED


def _getAllObjectsData(self, context, objects_listing):
    """ Returns the data in all files with a content object to be placed
        in a zipfile
    """
    import tempfile
    # Use temporary IO object instead of writing to filesystem.
    fd, path = tempfile.mkstemp('.zipfiletransport')
    close(fd)

    zipFile = ZipFile(path, 'w', ZIP_DEFLATED)
    context_path = str(context.virtual_url_path())

    for obj in objects_listing:
        object_extension = ''
        object_path = str(obj.virtual_url_path())
        is_image = self._objImplementsInterface(obj, interfaces.IATImage)
        is_file = self._objImplementsInterface(obj, interfaces.IATFile)
        if (is_image or is_file):
            file_data = str(obj.data)
            object_path = object_path.replace(context_path + '/', '')
            # Add an extension if we do not have one already
            if hasattr(obj, 'getContentType'):
                mime = obj.getContentType()

                if "image/jpeg" in mime:
                    object_extension = '.jpg'

                elif "image/png" in mime:
                    object_extension = '.png'

                elif "image/gif" in mime:
                    object_extension = '.gif'

                if object_extension in obj.getId():
                    object_extension = ''

        elif self._objImplementsInterface(obj, interfaces.IATDocument):

            if "text/html" == obj.Format():
                file_data = obj.getText()
                object_extension = ".html"

            elif "text/x-rst" == obj.Format():
                file_data = obj.getRawText()
                object_extension = ".rst"

            elif "text/structured" == obj.Format():
                file_data = obj.getRawText()
                object_extension = ".stx"

            elif "text/plain" == obj.Format():
                file_data = obj.getRawText()
                object_extension = ".txt"

            else:
                file_data = obj.getRawText()

            object_path = object_path.replace(context_path + '/', '')

        elif self._objImplementsInterface(obj, interfaces.IATFolder):
            if hasattr(obj, 'getRawText'):
                file_data = obj.getRawText()

                if object_path == context_path:
                    object_path = object_path.split("/")[-1]
                else:
                    object_path = object_path.replace(context_path + '/', '')

                if object_path[-5:] != ".html" and object_path[-4:] != ".htm":
                    object_extension = ".html"
        else:
            continue

        # start point for object path, adding 1 removes the initial '/'
        object_path = self.generateSafeFileName(object_path)
        if object_path:
            # reconstruct path with filename, restores non-ascii
            # characters in filenames
            filename_path = []
            for i in range(0, len(object_path.split('/'))):
                filename_path.append(obj.getId())
                obj = obj.aq_inner.aq_parent

            if len(filename_path) > 1:
                filename_path.reverse()
                filename_path = '/'.join(filename_path)
            else:
                filename_path = filename_path[0]

            # Add the correct file extension
            if filename_path[-len(object_extension):] != object_extension:
                filename_path += object_extension

            if 'Windows' in context.REQUEST['HTTP_USER_AGENT']:
                filename_path = filename_path.decode('utf-8').encode('cp437')
            zipFile.writestr(filename_path, file_data)

    zipFile.close()
    return path


def run():
    setattr(ZipFileTransportUtility, '_getAllObjectsData', _getAllObjectsData)
