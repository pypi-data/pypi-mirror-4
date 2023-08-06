import os
import json
import re
try:
    from urllib.parse import unquote, urlsplit, urlunsplit, urldefrag
except ImportError:     # Python 2
    from urllib import unquote
    from urlparse import urlsplit, urlunsplit, urldefrag

from django.utils.datastructures import SortedDict
from django.contrib.staticfiles.storage import CachedFilesMixin
from django.conf import settings
from django.contrib.staticfiles.utils import matches_patterns
from django.core.files.base import ContentFile
from django.utils.encoding import force_bytes, force_text

from storages.backends.s3boto import S3BotoStorage

class StaticS3Storage(S3BotoStorage, CachedFilesMixin):
    hash_filename='hash_mapping.json'
    def __init__(self, bucket=getattr(settings, 'AWS_STATIC_S3_BUCKET'),
                 custom_domain=getattr(settings, 'AWS_STATIC_S3_DOMAIN'),
                 url_protocol=getattr(settings, 'AWS_STATIC_URL_PROTOCOL')):
        S3BotoStorage.__init__(self, bucket=bucket,
                               custom_domain=custom_domain,
                               url_protocol=url_protocol,
                               secure_urls = url_protocol == 'https:')
        self.load_hashed_paths()
        self._patterns = SortedDict()
        for extension, patterns in self.patterns:
            for pattern in patterns:
                if isinstance(pattern, (tuple, list)):
                    pattern, template = pattern
                else:
                    template = self.default_template
                compiled = re.compile(pattern)
                self._patterns.setdefault(extension, []).append((compiled, template))

    #this method of completely copied from CachedFilesMixin
    #in order to create a new file instead of saving it to the cache
    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given list of files (called from collectstatic).

        Processing is actually two separate operations:

        1. renaming files to include a hash of their content for cache-busting,
           and copying those files to the target storage.
        2. adjusting files which contain references to other files so they
           refer to the cache-busting filenames.

        If either of these are performed on a file, then that file is considered
        post-processed.
        """
        # don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        # where to store the new paths
        self.hashed_paths = {}

        # build a list of adjustable files
        matches = lambda path: matches_patterns(path, self._patterns.keys())
        adjustable_paths = [path for path in paths if matches(path)]

        # then sort the files by the directory level
        path_level = lambda name: len(name.split(os.sep))
        
        for name in sorted(paths.keys(), key=path_level, reverse=True):

            # use the original, local file, not the copied-but-unprocessed
            # file, which might be somewhere far away, like S3
            storage, path = paths[name]
            with storage.open(path) as original_file:

                # generate the hash with the original content, even for
                # adjustable files.
                hashed_name = self.hashed_name(name, original_file)

                # then get the original's file content..
                if hasattr(original_file, 'seek'):
                    original_file.seek(0)

                hashed_file_exists = self.exists(hashed_name)
                processed = False

                # ..to apply each replacement pattern to the content
                if name in adjustable_paths:
                    content = original_file.read().decode(settings.FILE_CHARSET)
                    for patterns in self._patterns.values():
                        for pattern, template in patterns:
                            converter = self.url_converter(name, template)
                            content = pattern.sub(converter, content)
                    if hashed_file_exists:
                        self.delete(hashed_name)
                    # then save the processed result
                    content_file = ContentFile(force_bytes(content))
                    saved_name = self._save(hashed_name, content_file)
                    hashed_name = force_text(saved_name.replace('\\', '/'))
                    processed = True
                else:
                    # or handle the case in which neither processing nor
                    # a change to the original file happened
                    if not hashed_file_exists:
                        processed = True
                        saved_name = self._save(hashed_name, original_file)
                        hashed_name = force_text(saved_name.replace('\\', '/'))

                # and then set the cache accordingly
                self.hashed_paths[name.replace('\\', '/')] = hashed_name
                yield name, hashed_name, processed

        content_file = ContentFile(force_bytes(json.dumps(self.hashed_paths)))
        saved_name = self._save(self.hash_filename, content_file)
    
    def load_hashed_paths(self):
        try:
            json_file = self.open(self.hash_filename)
        except IOError:
            self.hashed_paths = {}
        else:
            self.hashed_paths = json.load(json_file)

    def get_hashed_name(self, name):
        return self.hashed_paths.get(name.replace('\\', '/'), None)

    def url(self, name, force=False):
        """
        Returns the real URL in DEBUG mode.
        """
        if settings.DEBUG and not force:
            hashed_name, fragment = name, ''
        else:
            clean_name, fragment = urldefrag(name)
            if urlsplit(clean_name).path.endswith('/'):  # don't hash paths
                hashed_name = name
            else:
                hashed_name = self.get_hashed_name(name)
                if hashed_name is None:
                    hashed_name = self.hashed_name(clean_name).replace('\\', '/')

        final_url = S3BotoStorage.url(self, hashed_name)

        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        query_fragment = '?#' in name  # [sic!]
        if fragment or query_fragment:
            urlparts = list(urlsplit(final_url))
            if fragment and not urlparts[4]:
                urlparts[4] = fragment
            if query_fragment and not urlparts[3]:
                urlparts[2] += '?'
            final_url = urlunsplit(urlparts)

        return unquote(final_url)

class MediaS3Storage(S3BotoStorage):
    
    def __init__(self, bucket=getattr(settings, 'AWS_MEDIA_S3_BUCKET'),
                 custom_domain=getattr(settings, 'AWS_MEDIA_S3_DOMAIN'),
                 url_protocol=getattr(settings, 'AWS_MEDIA_URL_PROTOCOL')):
        S3BotoStorage.__init__(self, bucket=bucket,
                               custom_domain=custom_domain,
                               url_protocol=url_protocol)
