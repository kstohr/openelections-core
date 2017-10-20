from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import os
import os.path
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from zipfile import ZipFile

from openelex.base.fetch import BaseFetcher
from openelex.us.sc.datasource import Datasource

class FetchResults(BaseFetcher):
    def __init__(self):
        super(FetchResults, self).__init__()
        self._datasource = Datasource()
        self._fetched = set()

    def fetch(self, url, fname=None, overwrite=False):
        # We keep track of URLs we've already fetched in this run since
        # there will be multiple output files mapped to a single zip
        # file.  If we've already fetched this URL, exit early.
        if url in self._fetched:
            return

        if url.endswith('.zip'):
            # Fetch the zip file, using the automatically generated filename
            zip_fname = self._local_zip_file_name(url)
            super(FetchResults, self).fetch(url, zip_fname, overwrite)
            self._extract_zip(url, zip_fname, overwrite)
        else:
            super(FetchResults, self).fetch(url, fname, overwrite)

        self._fetched.add(url)

    def _local_zip_file_name(self, url):
        """
        Return a normalized local file name for a results zip file.

        We don't care too much about the format because we can delete the
        zip file later.
        """
        parsed = urllib.parse.urlsplit(url)
        fname = parsed.path.split('/')[-1]
        return os.path.join(self.cache.abspath, fname)

    def _extract_zip(self, url, zip_fname=None, overwrite=False, remove=True):
        if zip_fname is None:
            zip_fname =  self._local_zip_file_name(url)

        with ZipFile(zip_fname, 'r') as zipf:
            for mapping in self._datasource.mappings_for_url(url):
                local_file_name = os.path.join(self.cache.abspath,
                    mapping['generated_filename'])
                if overwrite or not os.path.exists(local_file_name):
                    zipf.extract('detail.xml',
                        self.cache.abspath)
                    extracted_file_name = os.path.join(self.cache.abspath,
                        'detail.xml')
                    os.rename(extracted_file_name, local_file_name)
                    print("Added to cache: %s" % local_file_name)
                else:
                    print("File is cached: %s" % local_file_name)

        if remove:
            os.remove(zip_fname)
