"""

Module :mod:`pyesgf.download`
===================================

Tools for downloading files from ESGF.


"""

from urlparse import urlparse
import urllib2

import logging
log = logging.getLogger(__name__)

class BaseDownloadManager(object):
    """
    Manage downloads of single or multiple files.

    All methods that expect a download URL will either accept
    the URL as a string or any object that has the property
    ``download_url``.  E.g. instances of 
    :class:`pyesgf.search.result.FileResult` can be passed directly to
    :meth:`BaseDownloadManager.download` and instances of :class:`pesgf.search.result.ResultSet`
    can be passed directly to :meth:`BaseDownloadManager.download_all`.

    The destination of downloaded files can be controlled by subclassing and
    overriding :meth:`BaseDownloadManager.get_destination`.

    """

    def download_all(self, downloads):
        """
        Download a sequence or iterable of download URLs
        """

        raise NotImplementedError

    def download(self, download_obj):
        try:
            download_url = download_obj.download_url
        except AttributeError:
            download_url = str(download_obj)

        #---------------------------------------------------------------------
        # Basic sanity checking of URL
        url_p = urlparse(download_url)

        #!TODO: in future maybe support gsiftp
        if url_p.scheme not in ['http', 'https']:
            raise UnrecognisedUrlError('Unrecognised scheme %s in %s',
                                       repr(url_p.scheme), repr(url))

        dest = self.get_destination(download_obj)

        log.info('Begin download %s --> %s' % (download_url, dest))
        self.begin_download_hook()
        #!TODO: ..... fp urllib2.urlopen(

    def get_destination(self, download_obj):
        """
        :return: the destination file path for ``download_url``

        """
        raise NotImplementedError

    def begin_download_hook(self, download_url, destination):
        #!TODO
        pass
    

class SimpleDownloadManager(object):
    """
    A download manager that simply puts all files into a single directory.
    
    """
    def __init__(self, download_dir):
        self.download_dir = download_dir

    
